# import os


import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID, AuthorityInformationAccessOID

from bounca.certificate_engine.ssl.key import Key
from bounca.certificate_engine.ssl.repo import Repo
from bounca.x509_pki.models import Certificate as Certificate_model

one_day = datetime.timedelta(1, 0, 0)


class Certificate(object):

    def __init__(self, repo: Repo) -> None:
        if not isinstance(repo, Repo):
            raise RuntimeError("Provide a valid repo")
        self._repo = repo
        self._certificate = None

    @property
    def certificate(self):
        return self._certificate

    def create_certificate(self, cert: Certificate_model, private_key: Key) -> x509.Certificate:
        """
        Create a certificate.

        Arguments:
        Returns:   The certificate
        """

        public_key = private_key.key.public_key()
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, cert.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, cert.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, cert.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, cert.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, cert.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, cert.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(cert.dn.countryName)),
        ]))
        builder = builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, cert.dn.commonName),
        ]))

        builder = builder.not_valid_before(
            datetime.datetime(
                year=cert.created_at.year,
                month=cert.created_at.month,
                day=cert.created_at.day
            )
        )
        builder = builder.not_valid_after(
            datetime.datetime(
                year=cert.expires_at.year,
                month=cert.expires_at.month,
                day=cert.expires_at.day
            )
        )
        builder = builder.serial_number(int(cert.serial))
        builder = builder.public_key(public_key)

        if cert.crl_distribution_url:
            builder = builder.add_extension(
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

        builder = builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        builder = builder.add_extension(
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
        if cert.ocsp_distribution_host:
            builder = builder.add_extension(
                x509.AuthorityInformationAccess([
                    x509.AccessDescription(
                        AuthorityInformationAccessOID.OCSP,
                        x509.UniformResourceIdentifier(cert.ocsp_distribution_host)
                    )]),
                critical=True
            )

        # authorityKeyIdentifier = keyid:always, issuer
        builder = builder.add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(public_key),
            critical=True,
        )

        # subjectKeyIdentifier = hash
        builder = builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(public_key),
            critical=True,
        )

        certificate = builder.sign(
            private_key=private_key.key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )

        self._certificate = certificate
        return self._certificate

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

    def read_certificate(self, path: str) -> x509.Certificate:
        """
        Read certificate from repo

        Arguments: path - filename with relative path
        Returns:   The private key
        """
        _path = self._repo.make_repo_path(path)
        with open(_path, "rb") as f:
            pem = f.read()
        self._certificate = x509.load_pem_x509_certificate(pem, backend=default_backend())
        return self._certificate
