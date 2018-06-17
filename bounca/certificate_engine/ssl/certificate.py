# import os


import datetime
import ipaddress

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509 import DirectoryName
from cryptography.x509.extensions import _key_identifier_from_public_key
from cryptography.x509.oid import AuthorityInformationAccessOID, NameOID, ExtendedKeyUsageOID

from bounca.certificate_engine.ssl.key import Key
from bounca.x509_pki.models import Certificate as Certificate_model, DistinguishedName
from bounca.x509_pki.types import CertificateTypes


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
        return x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(dn.countryName)),
        ])

    def _set_issuer_name(self, cert: Certificate_model) -> None:
        dn = cert.parent.dn if cert.parent else cert.dn
        self._builder = self._builder.issuer_name(self._build_subject_names(dn))

    def _set_subject_name(self, cert: Certificate_model) -> None:
        self._builder = self._builder.subject_name(self._build_subject_names(cert.dn))

    def _set_public_key(self, cert: Certificate_model, private_key: Key, issuer_key: Key=None) -> None:
        self._builder = self._builder.public_key(private_key.key.public_key())
        root_cert = cert.parent if cert.parent and cert.type == CertificateTypes.INTERMEDIATE else \
            cert.parent.parent if cert.parent and cert.parent.parent and \
            (cert.type == CertificateTypes.SERVER_CERT or cert.type == CertificateTypes.CLIENT_CERT) else None
        root_ca_subject = [DirectoryName(self._build_subject_names(root_cert.dn))] if root_cert else None
        authority_cert_serial_number = int(cert.parent.serial) if root_cert else None
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
        if cert.type == CertificateTypes.SERVER_CERT or cert.type == CertificateTypes.CLIENT_CERT:
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
        if cert.type == CertificateTypes.SERVER_CERT or cert.type == CertificateTypes.CLIENT_CERT:
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
        path_length = 0 if cert.type == CertificateTypes.INTERMEDIATE else None
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
        # TODO implement checks
        # countryName = match
        # stateOrProvinceName = match
        # localityName = match
        # organizationName = match
        # organizationalUnitName = optional
        # commonName = supplied
        # emailAddress = optional
        if cert.parent.type != CertificateTypes.ROOT:
            raise RuntimeError("Multiple levels of intermediate certificates are not supported")

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)
        self._set_key_usage()
        return self._sign_certificate(issuer_key)

    def _create_server_certificate(self, cert: Certificate_model, private_key: Key,
                                   issuer_key: Key) -> x509.Certificate:
        # TODO implement checks
        # countryName = match
        # stateOrProvinceName = match
        # localityName = match
        # organizationName = match
        # organizationalUnitName = optional
        # commonName = supplied
        # emailAddress = optional
        if cert.parent.type != CertificateTypes.INTERMEDIATE and cert.parent.type != CertificateTypes.ROOT:
            raise RuntimeError("A root or intermediate parent is expected ")

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
                except:
                    pass
                try:
                    alt = x509.DNSName(altname)
                    alts.append(alt)
                    continue
                except:
                    pass

            self._builder = self._builder.add_extension(
                x509.SubjectAlternativeName(alts),
                critical=False,
            )

        return self._sign_certificate(issuer_key)

    def _create_client_certificate(self, cert: Certificate_model, private_key: Key,
                                   issuer_key: Key) -> x509.Certificate:
        # TODO implement checks
        # countryName = match
        # stateOrProvinceName = match
        # localityName = match
        # organizationName = match
        # organizationalUnitName = optional
        # commonName = supplied
        # emailAddress = optional
        if cert.parent.type != CertificateTypes.INTERMEDIATE and cert.parent.type != CertificateTypes.ROOT:
            raise RuntimeError("A root or intermediate parent is expected ")

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
                except:
                    pass

            self._builder = self._builder.add_extension(
                x509.SubjectAlternativeName(alts),
                critical=False,
            )

        return self._sign_certificate(issuer_key)

    def create_certificate(self, cert: Certificate_model, passphrase: bytes=None, passphrase_issuer: bytes=None) \
            -> 'Certificate':
        """
        Create a certificate.

        Arguments:
        Returns:   The certificate
        """

        try:
            private_key = Key().load(cert.key, passphrase)
        except ValueError:
            raise PassPhraseError("Bad passphrase, could not decode private key")

        try:
            if cert.parent:
                issuer_key = Key().load(cert.parent.key, passphrase_issuer)
        except ValueError:
            raise PassPhraseError("Bad passphrase, could not decode issuer key")

        if cert.type == CertificateTypes.ROOT:
            self._certificate = self._create_root_certificate(cert, private_key)
        elif cert.type == CertificateTypes.INTERMEDIATE:
            self._certificate = self._create_intermediate_certificate(cert, private_key, issuer_key)
        elif cert.type == CertificateTypes.SERVER_CERT:
            self._certificate = self._create_server_certificate(cert, private_key, issuer_key)
        elif cert.type == CertificateTypes.CLIENT_CERT:
            self._certificate = self._create_client_certificate(cert, private_key, issuer_key)

        return self

    def serialize(self, encoding: str=serialization.Encoding.PEM) -> bytes:
        """
        Serialize certificate

        Arguments: path - filename with relative path
                   encoding - optional different encoding
        Returns:   bytes
        """
        if not self._certificate:
            raise RuntimeError("No certificate object")

        return self._certificate.public_bytes(encoding=encoding)

    def load(self, pem: bytes) -> 'Certificate':
        """
        Read certificate from pem

        Arguments: pem - bytes with certificate
        Returns:   Self
        """

        self._certificate = x509.load_pem_x509_certificate(pem, backend=default_backend())
        return self
