# import os


import datetime
import ipaddress
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509 import DirectoryName
# noinspection PyProtectedMember,PyUnresolvedReferences
from cryptography.x509.extensions import _key_identifier_from_public_key
# noinspection PyUnresolvedReferences
from cryptography.x509.oid import AuthorityInformationAccessOID, ExtendedKeyUsageOID, NameOID
from functools import reduce

from certificate_engine.ssl.key import Key
from certificate_engine.types import (
    CertificateIntermediatePolicy, CertificatePolicy, CertificateRootPolicy, CertificateTypes)
from x509_pki.models import Certificate as Certificate_model
from x509_pki.models import DistinguishedName


class PassPhraseError(RuntimeError):
    """Base class for passphrase decode errors in this module."""
    pass


class PolicyError(ValueError):
    """Base class for policy errors in this module."""
    pass


class CertificateError(ValueError):
    """Base class for malformed certificates in this module."""
    pass


# noinspection PyTypeChecker
class Certificate(object):
    _certificate: x509.Certificate = None
    _builder: x509.CertificateBuilder = None

    @property
    def certificate(self):
        return self._certificate

    @staticmethod
    def _get_certificate_policy(cert: Certificate_model) -> CertificatePolicy:
        return CertificateRootPolicy() if cert.type == CertificateTypes.ROOT else \
            CertificateIntermediatePolicy() if cert.type == CertificateTypes.INTERMEDIATE else \
            CertificatePolicy()

    @staticmethod
    def _build_subject_names(cert: Certificate_model) -> x509.Name:
        dn = cert.dn
        policy = Certificate._get_certificate_policy(cert).policy
        attributes = []
        for attr in reduce(lambda x, y: x + y, [policy[k] for k in policy.keys()]):
            value = getattr(dn, attr[0])
            if attr[0] == 'countryName' and value is not None:
                value = getattr(value, 'code')
            if value is not None:
                attributes.append(x509.NameAttribute(attr[1], value))
        return x509.Name(attributes)

    @staticmethod
    def _check_common_name(cert: Certificate_model, common_name: str):
        if not cert.parent:
            return
        parent_crt = Certificate().load(cert.parent.keystore.crt).certificate
        if parent_crt.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == common_name:
            raise PolicyError("CommonName '{}' should not be equal to common name of parent".format(common_name))
        Certificate._check_common_name(cert.parent, common_name)

    @staticmethod
    def _check_policies_optional(dn: DistinguishedName, subject: dict, policy: CertificatePolicy):
        # noinspection PyUnresolvedReferences
        for attr in policy['optional']:
            if getattr(dn, attr[0]) is not None:
                subject[attr[0]] = getattr(dn, attr[0])

    @staticmethod
    def _check_policies_supplied(dn: DistinguishedName, subject: dict, policy: CertificatePolicy):
        # noinspection PyUnresolvedReferences
        for attr in policy['supplied']:
            if not getattr(dn, attr[0]):
                raise PolicyError("Attribute '{}' is required".format(attr[0]))
            subject[attr[0]] = getattr(dn, attr[0])

    @staticmethod
    def _check_policies(cert: Certificate_model):
        dn = cert.dn
        subject = {}
        if cert.dn.subjectAltNames:
            subject['subjectAltNames'] = cert.dn.subjectAltNames
        policy = Certificate._get_certificate_policy(cert).policy
        Certificate._check_policies_optional(dn, subject, policy)
        Certificate._check_policies_supplied(dn, subject, policy)
        if policy['match']:
            if not cert.parent:
                raise RuntimeError("Parent certificate is required")
            if not cert.parent.keystore.crt:
                raise RuntimeError("Parent certificate object has not been set")
            parent_crt = Certificate().load(cert.parent.keystore.crt).certificate
            for attr in policy['match']:
                if not parent_crt.subject.get_attributes_for_oid(attr[1]):
                    raise PolicyError("Attribute '{}' is not provided by parent".format(attr[0]))
                if parent_crt.subject.get_attributes_for_oid(attr[1])[0].value != getattr(dn, attr[0]):
                    raise PolicyError("Certificate should match field '{}' "
                                      "(issuer certificate: {}, certificate: {})"
                                      .format(attr[0], parent_crt.subject.get_attributes_for_oid(attr[1])[0].value,
                                              getattr(dn, attr[0])))
                subject[attr[0]] = getattr(dn, attr[0])
        Certificate._check_common_name(cert, getattr(dn, 'commonName'))
        cert.dn = DistinguishedName(**subject)

    @staticmethod
    def _check_issuer_provided(cert: Certificate_model):
        if not cert.parent:
            raise CertificateError("A parent certificate is expected")
        if cert.parent.type not in {CertificateTypes.INTERMEDIATE, CertificateTypes.ROOT}:
            raise CertificateError("A root or intermediate parent is expected")

    def _set_issuer_name(self, cert: Certificate_model) -> None:
        issuer_cert = cert.parent if cert.parent else cert
        self._builder = self._builder.issuer_name(Certificate._build_subject_names(issuer_cert))

    def _set_subject_name(self, cert: Certificate_model) -> None:
        self._builder = self._builder.subject_name(Certificate._build_subject_names(cert))

    def _set_public_key(self, cert: Certificate_model, private_key: Key, issuer_key: Key = None) -> None:
        self._builder = self._builder.public_key(private_key.key.public_key())
        issuer_cert_subject = issuer_cert_serial_number = None
        if cert.type != CertificateTypes.ROOT:
            issuer_cert = cert.parent
            issuer_cert_subject = [DirectoryName(Certificate._build_subject_names(issuer_cert))]
            issuer_cert_serial_number = int(issuer_cert.serial)
        self._builder = self._builder.add_extension(
            x509.AuthorityKeyIdentifier(key_identifier=_key_identifier_from_public_key(issuer_key.key.public_key()),
                                        authority_cert_issuer=issuer_cert_subject,
                                        authority_cert_serial_number=issuer_cert_serial_number),
            critical=True,
        )
        self._builder = self._builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.key.public_key()),
            critical=True,
        )

    def _set_crl_distribution_url(self, cert: Certificate_model) -> None:
        if cert.type in {CertificateTypes.SERVER_CERT, CertificateTypes.CLIENT_CERT}:
            cert = cert.parent
        if cert.crl_distribution_url:
            self._builder = self._builder.add_extension(
                x509.CRLDistributionPoints([
                    x509.DistributionPoint(
                        full_name=[x509.UniformResourceIdentifier(
                            'URI:{}{}{}.crl'.format(cert.crl_distribution_url,
                                                    "/" if not cert.crl_distribution_url.endswith("/") else "",
                                                    cert.slug_name)
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

    def _set_basic(self, cert: Certificate_model, private_key: Key,
                   issuer_key: Key) -> None:
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
        Certificate._check_policies(cert)

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, private_key)
        self._set_key_usage()
        return self._sign_certificate(private_key)

    def _create_intermediate_certificate(self, cert: Certificate_model, private_key: Key,
                                         issuer_key: Key) -> x509.Certificate:

        if cert.parent and cert.parent.type != CertificateTypes.ROOT:
            raise CertificateError("Parent is not a root certificate. "
                                   "Multiple levels of intermediate certificates are currently not supported")
        if cert.parent and cert.parent.parent:
            raise CertificateError("Parent certificate has a parent. "
                                   "Multiple levels of intermediate certificates are currently not supported")

        Certificate._check_policies(cert)

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)
        self._set_key_usage()
        return self._sign_certificate(issuer_key)

    def _create_server_certificate(self, cert: Certificate_model, private_key: Key,
                                   issuer_key: Key) -> x509.Certificate:

        Certificate._check_issuer_provided(cert)
        Certificate._check_policies(cert)

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

        Certificate._check_issuer_provided(cert)
        Certificate._check_policies(cert)

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

    def create_certificate(self, cert_request: Certificate_model, key: str, passphrase: str = None,
                           passphrase_issuer: str = None) \
            -> 'Certificate':
        """
        Create a certificate.

        Arguments: cert_request - The certificate request, containing all the information
                   passphrase - The passphrase of the key of the certificate
                   passphrase_issuer - The passphrase of the key of the signing certificate
        Returns:   The certificate object
        """

        try:
            private_key = Key().load(key, passphrase)
        except ValueError:
            raise PassPhraseError("Bad passphrase, could not decode private key")

        issuer_key = None
        try:
            if cert_request.parent:
                issuer_key = Key().load(cert_request.parent.keystore.key, passphrase_issuer)
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

    def serialize(self, encoding: serialization.Encoding = serialization.Encoding.PEM) -> str:
        """
        Serialize certificate

        Arguments: encoding - optional different encoding
        Returns:   bytes
        """
        if not self._certificate:
            raise RuntimeError("No certificate object")

        if encoding not in serialization.Encoding:
            raise ValueError("{} is not a valid encoding")

        return self._certificate.public_bytes(encoding=encoding).decode('utf8')

    def load(self, pem: str) -> 'Certificate':
        """
        Read certificate from pem

        Arguments: pem - bytes with certificate
        Returns:   Self
        """

        self._certificate = x509.load_pem_x509_certificate(pem.encode('utf8'), backend=default_backend())
        return self
