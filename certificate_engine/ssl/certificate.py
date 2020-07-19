# import os


import datetime
import ipaddress
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509 import DirectoryName
from cryptography.x509.extensions import _key_identifier_from_public_key
from cryptography.x509.oid import AuthorityInformationAccessOID, ExtendedKeyUsageOID, NameOID

from certificate_engine.ssl.key import Key
from certificate_engine.types import CertificateTypes
from x509_pki.models import Certificate as Certificate_model
from x509_pki.models import DistinguishedName


class PassPhraseError(RuntimeError):
    """Base class for passphrase decode errors in this module."""
    pass


class Certificate(object):

    def __init__(self) -> None:
        self._certificate = None  # type: x509.Certificate
        self._builder = None  # type: x509.CertificateBuilder

    @property
    def certificate(self):
        return self._certificate

    def _build_subject_names(self, dn: DistinguishedName) -> x509.Name:
        attributes = [
            x509.NameAttribute(NameOID.COMMON_NAME, dn.commonName)
        ]
        if dn.organizationName is not None:
            attributes.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, dn.organizationName))
        if dn.organizationalUnitName is not None:
            attributes.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, dn.organizationalUnitName))
        if dn.localityName is not None:
            attributes.append(x509.NameAttribute(NameOID.LOCALITY_NAME, dn.localityName))
        if dn.stateOrProvinceName is not None:
            attributes.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, dn.stateOrProvinceName))
        if dn.emailAddress is not None:
            attributes.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, dn.emailAddress))
        if dn.countryName.code is not None:
            attributes.append(x509.NameAttribute(NameOID.COUNTRY_NAME, dn.countryName.code))
        return x509.Name(attributes)

    def _set_issuer_name(self, cert: Certificate_model) -> None:
        dn = cert.parent.dn if cert.parent else cert.dn
        self._builder = self._builder.issuer_name(self._build_subject_names(dn))

    def _set_subject_name(self, cert: Certificate_model) -> None:
        self._builder = self._builder.subject_name(self._build_subject_names(cert.dn))

    def _get_root_cert(self, cert):
        return self._get_root_cert(cert.parent) if cert.parent else cert

    def _set_public_key(self, cert: Certificate_model, private_key: Key, issuer_key: Key = None) -> None:
        self._builder = self._builder.public_key(private_key.key.public_key())
        root_ca_subject = authority_cert_serial_number = None
        if cert.type != CertificateTypes.ROOT:
            root_cert = self._get_root_cert(cert.parent)
            root_ca_subject = [DirectoryName(self._build_subject_names(root_cert.dn))]
            authority_cert_serial_number = int(cert.parent.serial)
        self._builder = self._builder.add_extension(
            x509.AuthorityKeyIdentifier(key_identifier=_key_identifier_from_public_key(issuer_key.key.public_key()),
                                        authority_cert_issuer=root_ca_subject,
                                        authority_cert_serial_number=authority_cert_serial_number),
            critical=True,
        )
        self._builder = self._builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.key.public_key()),
            critical=True,
        )

    def _set_crl_distribution_url(self, cert: Certificate_model) -> None:
        if cert.type in {CertificateTypes.SERVER_CERT, cert.type == CertificateTypes.CLIENT_CERT}:
            cert = cert.parent
        if cert.crl_distribution_url:
            self._builder = self._builder.add_extension(
                x509.CRLDistributionPoints([
                    x509.DistributionPoint(
                        full_name=[x509.UniformResourceIdentifier(
                            'URI:{}{}{}.crl'.format(cert.crl_distribution_url,
                                                    "/" if not cert.crl_distribution_url.endswith("/") else "",
                                                    cert.shortname)
                        )],
                        relative_name=None,
                        reasons=frozenset([
                            x509.ReasonFlags.key_compromise,
                            x509.ReasonFlags.ca_compromise,
                            x509.ReasonFlags.affiliation_changed,
                            x509.ReasonFlags.superseded,
                            x509.ReasonFlags.privilege_withdrawn,
                            x509.ReasonFlags.cessation_of_operation,
                            x509.ReasonFlags.aa_compromise,
                            x509.ReasonFlags.certificate_hold,
                        ]),
                        crl_issuer=None
                    )]),
                critical=True
            )

    def _set_ocsp_distribution_url(self, cert: Certificate_model) -> None:
        if cert.type in {CertificateTypes.SERVER_CERT, cert.type == CertificateTypes.CLIENT_CERT}:
            cert = cert.parent
        if cert.ocsp_distribution_host:
            self._builder = self._builder.add_extension(
                x509.AuthorityInformationAccess([
                    x509.AccessDescription(
                        AuthorityInformationAccessOID.OCSP,
                        x509.UniformResourceIdentifier(cert.ocsp_distribution_host)
                    )]),
                critical=True
            )

    def _set_basic_constraints(self, cert: Certificate_model) -> None:
        path_length = None
        if cert.type == CertificateTypes.INTERMEDIATE:
            path_length = 0  # TODO check with multiple intermediates
        ca = cert.type == CertificateTypes.ROOT or cert.type == CertificateTypes.INTERMEDIATE
        self._builder = self._builder.add_extension(
            x509.BasicConstraints(ca=ca, path_length=path_length),
            critical=ca,
        )

    def _set_key_usage(self) -> None:
        self._builder = self._builder.add_extension(
            x509.KeyUsage(digital_signature=True,
                          content_commitment=False,
                          key_encipherment=False,
                          data_encipherment=False,
                          key_agreement=False,
                          key_cert_sign=True,
                          crl_sign=True,
                          encipher_only=False,
                          decipher_only=False
                          ),
            critical=True,
        )

    def _set_dates(self, cert: Certificate_model) -> None:
        self._builder = self._builder.not_valid_before(
            datetime.datetime(
                year=cert.created_at.year,
                month=cert.created_at.month,
                day=cert.created_at.day
            )
        )
        self._builder = self._builder.not_valid_after(
            datetime.datetime(
                year=cert.expires_at.year,
                month=cert.expires_at.month,
                day=cert.expires_at.day
            )
        )

    def _set_basic(self, cert: Certificate_model, private_key: Key, issuer_key: Key) -> None:
        self._builder = self._builder.serial_number(int(cert.serial))
        self._set_issuer_name(cert)
        self._set_dates(cert)
        self._set_subject_name(cert)
        self._set_public_key(cert, private_key, issuer_key)
        self._set_crl_distribution_url(cert)
        self._set_ocsp_distribution_url(cert)
        self._set_basic_constraints(cert)

    def _sign_certificate(self, private_key: Key) -> x509.Certificate:
        return self._builder.sign(
            private_key=private_key.key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )

    def _create_root_certificate(self, cert: Certificate_model, private_key: Key) -> x509.Certificate:
        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, private_key)
        self._set_key_usage()
        return self._sign_certificate(private_key)

    def _create_intermediate_certificate(self, cert: Certificate_model, private_key: Key,
                                         issuer_key: Key) -> x509.Certificate:

        root_crt = Certificate().load(cert.parent.crt).certificate

        # TODO Test this
        if root_crt.type != CertificateTypes.ROOT or root_crt.parent:
            raise RuntimeError("Multiple levels of intermediate certificates are currently not supported")
        if root_crt.parent:
            raise RuntimeError("Multiple levels of intermediate certificates are not supported")

        # The root CA should only sign intermediate certificates that match.
        for e in [(NameOID.COUNTRY_NAME, "countryName"), (NameOID.STATE_OR_PROVINCE_NAME, "stateOrProvinceName"),
                  (NameOID.ORGANIZATION_NAME, "organizationName")]:
            if not root_crt.subject.get_attributes_for_oid(e[0]):
                raise RuntimeError("Root certificate has no attribute {} field {}"
                                   .format(e[0], e[1]))
            if root_crt.subject.get_attributes_for_oid(e[0])[0].value != getattr(cert.dn, e[1]):
                raise ValueError("Intermediate certificate should match field {} "
                                 "(root cert: {}, intermediate cert: {})"
                                 .format(e[1], root_crt.subject.get_attributes_for_oid(e[0])[0].value,
                                         getattr(cert.dn, e[1])))

        if not cert.dn.commonName:
            raise ValueError("CommonName has not been supplied")

        # TODO make test
        if root_crt.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == cert.dn.commonName:
            raise ValueError("CommonName {} should not be equal to common name of rootcert".format(cert.dn.commonName))

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)
        self._set_key_usage()
        return self._sign_certificate(issuer_key)

    def _create_server_certificate(self, cert: Certificate_model, private_key: Key,
                                   issuer_key: Key) -> x509.Certificate:

        if cert.parent.type not in {CertificateTypes.INTERMEDIATE, CertificateTypes.ROOT}:
            raise RuntimeError("A root or intermediate parent is expected ")

        if not cert.dn.commonName:
            raise ValueError("CommonName has not been supplied")

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)

        self._builder = self._builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        )

        self._builder = self._builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )

        if cert.dn.subjectAltNames:
            alts = []
            for altname in cert.dn.subjectAltNames:
                try:
                    alt = x509.IPAddress(ipaddress.ip_address(altname))
                    alts.append(alt)
                    continue
                except ValueError:
                    pass
                try:
                    alt = x509.DNSName(altname)
                    alts.append(alt)
                    continue
                except ValueError:
                    pass

            self._builder = self._builder.add_extension(
                x509.SubjectAlternativeName(alts),
                critical=False,
            )

        return self._sign_certificate(issuer_key)

    def _create_client_certificate(self, cert: Certificate_model, private_key: Key,
                                   issuer_key: Key) -> x509.Certificate:

        if cert.parent.type not in {CertificateTypes.INTERMEDIATE, CertificateTypes.ROOT}:
            raise RuntimeError("A root or intermediate parent is expected ")

        if not cert.dn.commonName:
            raise ValueError("CommonName has not been supplied")

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)

        self._builder = self._builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        )

        self._builder = self._builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH, ExtendedKeyUsageOID.EMAIL_PROTECTION]),
            critical=False,
        )

        if cert.dn.subjectAltNames:
            alts = []
            for altname in cert.dn.subjectAltNames:
                try:
                    alt = x509.RFC822Name(altname)
                    alts.append(alt)
                    continue
                except ValueError:
                    pass

            self._builder = self._builder.add_extension(
                x509.SubjectAlternativeName(alts),
                critical=False,
            )

        return self._sign_certificate(issuer_key)

    def create_certificate(self, cert_request: Certificate_model, passphrase: bytes = None,
                           passphrase_issuer: bytes = None) \
            -> 'Certificate':
        """
        Create a certificate.

        Arguments: cert_request - The certificate request, containing all the information
                   passphrase - The passphrase of the key of the certificate
                   passphrase_issuer - The passphrase of the key of the signing certificate
        Returns:   The certificate object
        """

        try:
            private_key = Key().load(cert_request.key, passphrase)
        except ValueError:
            raise PassPhraseError("Bad passphrase, could not decode private key")

        try:
            if cert_request.parent:
                issuer_key = Key().load(cert_request.parent.key, passphrase_issuer)
        except ValueError:
            raise PassPhraseError("Bad passphrase, could not decode issuer key")

        if cert_request.type == CertificateTypes.ROOT:
            self._certificate = self._create_root_certificate(cert_request, private_key)
        elif cert_request.type == CertificateTypes.INTERMEDIATE:
            self._certificate = self._create_intermediate_certificate(cert_request, private_key, issuer_key)
        elif cert_request.type == CertificateTypes.SERVER_CERT:
            self._certificate = self._create_server_certificate(cert_request, private_key, issuer_key)
        elif cert_request.type == CertificateTypes.CLIENT_CERT:
            self._certificate = self._create_client_certificate(cert_request, private_key, issuer_key)
        return self

    def serialize(self, encoding: str = serialization.Encoding.PEM) -> bytes:
        """
        Serialize certificate

        Arguments: encoding - optional different encoding
        Returns:   bytes
        """
        if not self._certificate:
            raise RuntimeError("No certificate object")

        # TODO test
        if encoding not in serialization.Encoding:
            raise ValueError("{} is not a valid encoding")

        return self._certificate.public_bytes(encoding=encoding)

    def load(self, pem: bytes) -> 'Certificate':
        """
        Read certificate from pem

        Arguments: pem - bytes with certificate
        Returns:   Self
        """

        self._certificate = x509.load_pem_x509_certificate(pem, backend=default_backend())
        return self
