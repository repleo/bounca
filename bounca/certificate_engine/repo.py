
import os
import shutil

from cryptography.hazmat.backends import default_backend
from django.conf import settings
from cryptography.hazmat.primitives import serialization

REPO_PATH = settings.CERTIFICATE_REPO_PATH


class Repo(object):
    """ Repo handler for certificate files """

    @staticmethod
    def create(path=REPO_PATH):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def delete(path=REPO_PATH):
        shutil.rmtree(path)

    def __init__(self, path=REPO_PATH):
        self.base = path
        self.create(path)

    def write_private_key(self, key, path, passphrase=None, encoding=serialization.Encoding.PEM):
        _path = os.path.join(self.base, path)
        encryption = serialization.BestAvailableEncryption(passphrase) if passphrase else serialization.NoEncryption
        with open(_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=encoding,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encryption,
            ))

    def read_private_key(self, path, passphrase=None):
        _path = os.path.join(self.base, path)
        with open(_path, "rb") as f:
            pem = f.read()
        return serialization.load_pem_private_key(pem, passphrase, backend=default_backend())

    def check_passphrase(self, path, passphrase=None):
        try:
            self.read_private_key(path, passphrase)
            return True
        except ValueError as e:
            if str(e) == 'Bad decrypt. Incorrect password?':
                return False
            raise e
