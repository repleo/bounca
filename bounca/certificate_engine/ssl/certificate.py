# import os


import datetime
import uuid

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID

from bounca.certificate_engine.ssl.key import Key
from bounca.certificate_engine.ssl.repo import Repo


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

    def create_certificate(self, private_key: Key) -> None:
        """
        Create a certificate.

        Arguments:
        Returns:   The certificate
        """
        public_key = private_key.key.public_key()

        builder = x509.CertificateBuilder()
        builder = builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'openstack-ansible Test CA'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'openstack-ansible'),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u'Default CA Deployment'),
        ]))
        builder = builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'openstack-ansible Test CA'),
        ]))
        builder = builder.not_valid_before(datetime.datetime.today() - one_day)
        builder = builder.not_valid_after(datetime.datetime(2018, 8, 2))
        builder = builder.serial_number(int(uuid.uuid4()))
        builder = builder.public_key(public_key)
        builder = builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        )
        certificate = builder.sign(
            private_key=private_key.key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )
        print(isinstance(certificate, x509.Certificate))
        print(certificate.public_bytes(
            encoding=serialization.Encoding.PEM,
        ))
        return self._certificate

# print(isinstance(certificate, x509.Certificate))
#
# with open("ca.key", "wb") as f:
#     f.write(private_key.private_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PrivateFormat.TraditionalOpenSSL,
#         encryption_algorithm=serialization.BestAvailableEncryption(b"openstack-ansible")
#     ))
#
# with open("ca.crt", "wb") as f:
#     f.write(certificate.public_bytes(
#         encoding=serialization.Encoding.PEM,
#     ))
