from __future__ import annotations

import copy
import datetime
import ipaddress
from typing import TYPE_CHECKING, List, Optional

import arrow
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed448, ed25519
from cryptography.x509 import DirectoryName, GeneralName

# noinspection PyProtectedMember,PyUnresolvedReferences
from cryptography.x509.extensions import _key_identifier_from_public_key

# noinspection PyUnresolvedReferences
from cryptography.x509.oid import AuthorityInformationAccessOID, ExtendedKeyUsageOID, NameOID

from certificate_engine.ssl.key import Key
from certificate_engine.types import (
    CertificateBasePolicy,
    CertificateIntermediatePolicy,
    CertificatePolicy,
    CertificateRootPolicy,
    CertificateTypes,
)

if TYPE_CHECKING:
    from x509_pki.models import Certificate as CertificateType
    from x509_pki.models import DistinguishedName
    from x509_pki.models import DistinguishedName as DistinguishedNameType
else:
    CertificateType = object
    DistinguishedNameType = object


class PassPhraseError(RuntimeError):
    """Base class for passphrase decode errors in this module."""

    pass


class PolicyError(ValueError):
    """Base class for policy errors in this module."""

    pass


class CertificateError(ValueError):
    """Base class for malformed certificates in this module."""

    pass


class Certificate(object):
    _certificate: Optional[x509.Certificate] = None
    _builder: x509.CertificateBuilder

    @property
    def certificate(self):
        if self._certificate is None:
            raise RuntimeError("No certificate object")
        return self._certificate

    @staticmethod
    def _get_certificate_policy(cert: CertificateType) -> CertificateBasePolicy:
        return (
            CertificateRootPolicy()
            if cert.type == CertificateTypes.ROOT
            else CertificateIntermediatePolicy() if cert.type == CertificateTypes.INTERMEDIATE else CertificatePolicy()
        )

    @staticmethod
    def build_subject_names(cert: CertificateType) -> x509.Name:
        dn = cert.dn
        fields = Certificate._get_certificate_policy(cert).fields_dn
        attributes = []
        for field in fields:
            name = field[0]
            x509attr = field[1]
            value = getattr(dn, name)
            if name == "countryName" and value:
                value = getattr(value, "code")
            if value and x509attr is not None:
                attributes.append(x509.NameAttribute(x509attr, value))
        return x509.Name(attributes)

    @staticmethod
    def _check_common_name(cert: CertificateType, common_name: str):
        if not cert.parent:
            return
        parent_crt = Certificate().load(cert.parent.keystore.crt).certificate
        if parent_crt.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == common_name:
            raise PolicyError("CommonName '{}' should not be equal to common name of parent".format(common_name))
        Certificate._check_common_name(cert.parent, common_name)

    @staticmethod
    def _check_policies_optional(dn: DistinguishedName, cp: CertificateBasePolicy):
        attributes = [attr for attr in cp.policy["optional"] + cp.policy["supplied"] + cp.policy["match"]]
        for key in list(dn.__dict__):
            if not key.startswith("_") and key not in attributes:
                setattr(dn, key, None)

    @staticmethod
    def _check_policies_supplied(dn: DistinguishedName, cp: CertificateBasePolicy):
        # noinspection PyUnresolvedReferences
        for attr in cp.policy["supplied"]:
            if not getattr(dn, attr):
                raise PolicyError({f"dn__{attr}": f"Attribute '{attr}' is required by policy"})

    @staticmethod
    def _lookup_x509_attr(attr: str, cp: CertificateBasePolicy):
        for attr_tuple in cp.fields_dn:
            if attr_tuple[0] == attr:
                return attr_tuple[1]
        raise ValueError(f"Attribute {attr} not found in certificate policy fields")

    @staticmethod
    def _check_policies(cert: CertificateType):
        dn = cert.dn
        cp = Certificate._get_certificate_policy(cert)
        Certificate._check_policies_optional(dn, cp)
        Certificate._check_policies_supplied(dn, cp)
        if cp.policy["match"]:
            if not cert.parent:
                raise RuntimeError("Parent certificate is required")
            if not cert.parent.keystore.crt:
                raise RuntimeError("Parent certificate object has not been set")
            parent_crt = Certificate().load(cert.parent.keystore.crt).certificate
            for attr in cp.policy["match"]:
                x509_attr = Certificate._lookup_x509_attr(attr, cp)
                if not parent_crt.subject.get_attributes_for_oid(x509_attr):
                    raise PolicyError("Attribute '{}' is not provided by parent".format(attr))

                if parent_crt.subject.get_attributes_for_oid(x509_attr)[0].value != getattr(dn, attr):
                    raise PolicyError(
                        "Certificate should match field '{}' "
                        "(issuer certificate: {}, certificate: {})".format(
                            attr, parent_crt.subject.get_attributes_for_oid(x509_attr)[0].value, getattr(dn, attr)
                        )
                    )
        Certificate._check_common_name(cert, getattr(dn, "commonName"))

    @staticmethod
    def _check_issuer_provided(cert: CertificateType):
        if not cert.parent:
            raise CertificateError("A parent certificate is expected")
        if cert.parent.type not in {CertificateTypes.INTERMEDIATE, CertificateTypes.ROOT}:
            raise CertificateError("A root or intermediate parent is expected")

    def _set_issuer_name(self, cert: CertificateType) -> None:
        issuer_cert = cert.parent if cert.parent else cert
        self._builder = self._builder.issuer_name(Certificate.build_subject_names(issuer_cert))

    def _set_subject_name(self, cert: CertificateType) -> None:
        self._builder = self._builder.subject_name(Certificate.build_subject_names(cert))

    def _set_public_key(self, cert: CertificateType, private_key: Key, issuer_key: Key) -> None:
        self._builder = self._builder.public_key(private_key.key.public_key())
        ca_issuer_cert_subject = ca_issuer_cert_serial_number = None
        if cert.type not in [CertificateTypes.ROOT, CertificateTypes.INTERMEDIATE]:
            ca_issuer_cert = cert.parent.parent if cert.parent.parent else cert.parent
            issuer_cert = cert.parent
            ca_issuer_cert_subject = [DirectoryName(Certificate.build_subject_names(ca_issuer_cert))]
            ca_issuer_cert_serial_number = int(issuer_cert.serial)
        self._builder = self._builder.add_extension(
            x509.AuthorityKeyIdentifier(
                key_identifier=_key_identifier_from_public_key(issuer_key.key.public_key()),
                authority_cert_issuer=ca_issuer_cert_subject,
                authority_cert_serial_number=ca_issuer_cert_serial_number,
            ),
            critical=False,
        )
        self._builder = self._builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.key.public_key()),
            critical=False,
        )

    def _set_crl_distribution_url(self, cert: CertificateType) -> None:
        if cert.type is not CertificateTypes.ROOT:
            cert = cert.parent
            crl_distribution_url = cert.crl_distribution_url
            if crl_distribution_url:
                self._builder = self._builder.add_extension(
                    x509.CRLDistributionPoints(
                        [
                            x509.DistributionPoint(
                                full_name=[x509.UniformResourceIdentifier(crl_distribution_url)],
                                relative_name=None,
                                reasons=None,
                                crl_issuer=None,
                            )
                        ]
                    ),
                    critical=False,
                )

    def _set_ocsp_distribution_url(self, cert: CertificateType) -> None:
        if cert.type is not CertificateTypes.ROOT:
            cert = cert.parent
            if cert.ocsp_distribution_host:
                self._builder = self._builder.add_extension(
                    x509.AuthorityInformationAccess(
                        [
                            x509.AccessDescription(
                                AuthorityInformationAccessOID.OCSP,
                                x509.UniformResourceIdentifier(cert.ocsp_distribution_host),
                            )
                        ]
                    ),
                    critical=False,
                )

    def _set_basic_constraints(self, cert: CertificateType) -> None:
        path_length = None
        if cert.type == CertificateTypes.INTERMEDIATE:
            path_length = 0
        ca = cert.type in [CertificateTypes.ROOT, CertificateTypes.INTERMEDIATE]
        self._builder = self._builder.add_extension(
            x509.BasicConstraints(ca=ca, path_length=path_length),
            critical=ca,
        )

    def _set_key_usage(self) -> None:
        self._builder = self._builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )

    def _set_dates(self, cert: CertificateType) -> None:
        self._builder = self._builder.not_valid_before(
            arrow.get(
                datetime.datetime(year=cert.created_at.year, month=cert.created_at.month, day=cert.created_at.day)
            )
            .shift(days=-1)
            .datetime
        )
        self._builder = self._builder.not_valid_after(
            datetime.datetime(year=cert.expires_at.year, month=cert.expires_at.month, day=cert.expires_at.day)
        )

    def _set_basic(self, cert: CertificateType, private_key: Key, issuer_key: Key) -> None:
        self._builder = self._builder.serial_number(int(cert.serial))
        self._set_issuer_name(cert)
        self._set_dates(cert)
        self._set_subject_name(cert)
        self._set_public_key(cert, private_key, issuer_key)
        self._set_crl_distribution_url(cert)
        self._set_ocsp_distribution_url(cert)
        self._set_basic_constraints(cert)

    def _sign_certificate(self, private_key: Key) -> x509.Certificate:
        algorithm = (
            None if isinstance(private_key.key, (ed25519.Ed25519PrivateKey, ed448.Ed448PrivateKey)) else hashes.SHA256()
        )

        return self._builder.sign(private_key=private_key.key, algorithm=algorithm, backend=default_backend())

    def _create_root_certificate(self, cert: CertificateType, private_key: Key) -> x509.Certificate:
        Certificate._check_policies(cert)

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, private_key)
        self._set_key_usage()
        return self._sign_certificate(private_key)

    def _create_intermediate_certificate(
        self, cert: CertificateType, private_key: Key, issuer_key: Key
    ) -> x509.Certificate:
        if cert.parent and cert.parent.type != CertificateTypes.ROOT:
            raise CertificateError(
                "Parent is not a root certificate. "
                "Multiple levels of intermediate certificates are currently not supported"
            )
        if cert.parent and cert.parent.parent:
            raise CertificateError(
                "Parent certificate has a parent. "
                "Multiple levels of intermediate certificates are currently not supported"
            )

        Certificate._check_policies(cert)

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)
        self._set_key_usage()
        return self._sign_certificate(issuer_key)

    def _create_server_certificate(self, cert: CertificateType, private_key: Key, issuer_key: Key) -> x509.Certificate:
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
                decipher_only=False,
            ),
            critical=True,
        )

        self._builder = self._builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )

        if cert.dn.subjectAltNames:
            alts: List[GeneralName] = []
            for altname in cert.dn.subjectAltNames:
                try:
                    alt_ip = x509.IPAddress(ipaddress.ip_address(altname))
                    alts.append(alt_ip)
                    continue
                except ValueError:
                    pass
                try:
                    alt_dns = x509.DNSName(altname)
                    alts.append(alt_dns)
                    continue
                except ValueError:
                    pass

            self._builder = self._builder.add_extension(
                x509.SubjectAlternativeName(alts),
                critical=False,
            )

        return self._sign_certificate(issuer_key)

    def _create_client_certificate(self, cert: CertificateType, private_key: Key, issuer_key: Key) -> x509.Certificate:
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
                decipher_only=False,
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

    def _create_ocsp_certificate(self, cert: CertificateType, private_key: Key, issuer_key: Key) -> x509.Certificate:
        Certificate._check_issuer_provided(cert)
        Certificate._check_policies(cert)
        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)
        self._builder = self._builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )

        self._builder = self._builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.OCSP_SIGNING]),
            critical=True,
        )

        return self._sign_certificate(issuer_key)

    def _create_code_signing_certificate(
        self, cert: CertificateType, private_key: Key, issuer_key: Key
    ) -> x509.Certificate:
        Certificate._check_issuer_provided(cert)
        Certificate._check_policies(cert)
        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)
        self._builder = self._builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )

        self._builder = self._builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CODE_SIGNING]),
            critical=True,
        )

        return self._sign_certificate(issuer_key)

    def check_policies(self, cert_request: CertificateType):
        self._check_policies(copy.deepcopy(cert_request))

    @staticmethod
    def _get_issuer_key(cert_request, passphrase_issuer):
        issuer_key = None
        try:
            if cert_request.parent:
                issuer_key = Key().load(cert_request.parent.keystore.key, passphrase_issuer)
        except (ValueError, TypeError):
            raise PassPhraseError("Bad passphrase, could not decode issuer key")
        return issuer_key

    @staticmethod
    def _get_key(key, passphrase):
        try:
            return Key().load(key, passphrase)
        except ValueError:
            raise PassPhraseError("Bad passphrase, could not decode private key")

    def create_certificate(
        self,
        cert_request: CertificateType,
        key: str,
        passphrase: Optional[str] = None,
        passphrase_issuer: Optional[str] = None,
    ) -> Certificate:
        """
        Create a certificate.

        Arguments: cert_request - The certificate request, containing all the information
                   passphrase - The passphrase of the key of the certificate
                   passphrase_issuer - The passphrase of the key of the signing certificate
        Returns:   The certificate object
        """

        private_key = self._get_key(key, passphrase)
        issuer_key = self._get_issuer_key(cert_request, passphrase_issuer)

        if cert_request.type == CertificateTypes.ROOT:
            self._certificate = self._create_root_certificate(cert_request, private_key)
        elif cert_request.type == CertificateTypes.INTERMEDIATE:
            self._certificate = self._create_intermediate_certificate(cert_request, private_key, issuer_key)
        elif cert_request.type == CertificateTypes.SERVER_CERT:
            self._certificate = self._create_server_certificate(cert_request, private_key, issuer_key)
        elif cert_request.type == CertificateTypes.CLIENT_CERT:
            self._certificate = self._create_client_certificate(cert_request, private_key, issuer_key)
        elif cert_request.type == CertificateTypes.CODE_SIGNING_CERT:
            self._certificate = self._create_code_signing_certificate(cert_request, private_key, issuer_key)
        elif cert_request.type == CertificateTypes.OCSP:
            self._certificate = self._create_ocsp_certificate(cert_request, private_key, issuer_key)
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

        return self._certificate.public_bytes(encoding=encoding).decode("utf8")

    def load(self, pem: str) -> Certificate:
        """
        Read certificate from pem

        Arguments: pem - Bytes with certificate
        Returns:   Self
        """

        self._certificate = x509.load_pem_x509_certificate(pem.encode("utf8"), backend=default_backend())
        return self
