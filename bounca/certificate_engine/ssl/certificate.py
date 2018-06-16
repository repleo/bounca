# import os


import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import AuthorityInformationAccessOID, NameOID

from bounca.certificate_engine.ssl.key import Key
from bounca.certificate_engine.ssl.repo import Repo
from bounca.x509_pki.models import Certificate as Certificate_model
from bounca.x509_pki.types import CertificateTypes


one_day = datetime.timedelta(1, 0, 0)


class Certificate(object):

    def __init__(self, repo: Repo) -> None:
        if not isinstance(repo, Repo):
            raise RuntimeError("Provide a valid repo")
        self._repo = repo
        self._certificate = None
        self._builder = None

    @property
    def certificate(self):
        return self._certificate

    def _set_subject_name(self, cert: Certificate_model) -> None:
        self._builder = self._builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, cert.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, cert.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, cert.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, cert.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, cert.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, cert.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(cert.dn.countryName)),
        ]))

    def _set_public_key(self, private_key: Key, issuer_key: Key=None) -> None:
        self._builder = self._builder.public_key(private_key.key.public_key())
        self._builder = self._builder.add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_key.key.public_key()),
            critical=True,
        )
        self._builder = self._builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.key.public_key()),
            critical=True,
        )

    def _set_crl_distribution_url(self, cert: Certificate_model) -> None:
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
        self._builder = self._builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=path_length),
            critical=True,
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

    def _set_common_name(self, cert: Certificate_model) -> None:
        self._builder = self._builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, cert.dn.commonName),
        ]))

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
        self._set_common_name(cert)
        self._set_dates(cert)
        self._set_subject_name(cert)
        self._set_public_key(private_key, issuer_key)
        self._set_crl_distribution_url(cert)
        self._set_ocsp_distribution_url(cert)
        self._set_basic_constraints(cert)
        self._set_key_usage()

    def _sign_certificate(self, private_key: Key) -> x509.Certificate:
        return self._builder.sign(
            private_key=private_key.key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )

    def _create_root_certificate(self, cert: Certificate_model, private_key: Key) -> x509.Certificate:
        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, private_key)
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

        self._builder = x509.CertificateBuilder()
        self._set_basic(cert, private_key, issuer_key)
        return self._sign_certificate(issuer_key)

    def create_certificate(self, cert: Certificate_model, private_key: Key,
                           root_cert: Certificate_model=None, issuer_key: Key=None) \
            -> 'Certificate':
        """
        Create a certificate.

        Arguments:
        Returns:   The certificate
        """
        if cert.type == CertificateTypes.ROOT:
            self._certificate = self._create_root_certificate(cert, private_key)
        elif cert.type == CertificateTypes.INTERMEDIATE:
            if not issuer_key:
                raise RuntimeError("Expect issuer key")
            self._certificate = self._create_intermediate_certificate(cert, private_key, issuer_key)
        elif cert.type == CertificateTypes.SERVER_CERT:
            if not issuer_key:
                raise RuntimeError("Expect issuer key")
            self._certificate = self._create_server_certificate(cert, private_key, issuer_key)

        return self

    def write_certificate(self, path: str, encoding: str=serialization.Encoding.PEM) -> None:
        """
        Write certificate to repo

        Arguments: path - filename with relative path
                   encoding - optional different encoding
        Returns:   None
        """
        if not self._certificate:
            raise RuntimeError("No certificate object")

        _path = self._repo.make_repo_path(path)

        with open(_path, "wb") as f:
            f.write(self._certificate.public_bytes(encoding=encoding))

    def read_certificate(self, path: str) -> 'Certificate':
        """
        Read certificate from repo

        Arguments: path - filename with relative path
        Returns:   The private key
        """
        _path = self._repo.make_repo_path(path)
        with open(_path, "rb") as f:
            pem = f.read()
        self._certificate = x509.load_pem_x509_certificate(pem, backend=default_backend())
        return self
