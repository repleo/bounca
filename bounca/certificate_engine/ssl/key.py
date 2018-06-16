import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from bounca.certificate_engine.ssl.repo import Repo


class Key(object):

    def __init__(self, repo: Repo) -> None:
        if not isinstance(repo, Repo):
            raise RuntimeError("Provide a valid repo")
        self._repo = repo
        self._key = None  # type: RSAPrivateKey

    @property
    def key(self) -> RSAPrivateKey:
        return self._key

    def create_key(self, key_size: int) -> RSAPrivateKey:
        """
        Create a public/private key pair.

        Arguments: key_size - Number of bits to use in the key
        Returns:   The private key
        """
        self._key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        return self._key

    def write_private_key(self, path: str, passphrase: bytes=None, encoding: str=serialization.Encoding.PEM) -> None:
        """
        Write key to repo

        Arguments: path - filename with relative path
                   passphrase - optional passphrase (must be bytes)
                   encoding - optional different encoding
        Returns:   None
        """

        if not self._key:
            raise RuntimeError("No key object")

        _path = self._repo.make_repo_path(path)
        # Make file writable for update
        if os.path.isfile(_path):
            os.chmod(_path, 0o600)
        encryption = serialization.BestAvailableEncryption(passphrase) if passphrase else serialization.NoEncryption()
        with open(_path, "wb") as f:
            f.write(self._key.private_bytes(
                encoding=encoding,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encryption,
            ))
        # Make private key only readable by myself
        os.chmod(_path, 0o400)

    def read_private_key(self, path: str, passphrase: bytes=None) -> RSAPrivateKey:
        """
        Read key from repo

        Arguments: path - filename with relative path
                   passphrase - optional passphrase (must be bytes)
        Returns:   The private key
        """

        _path = self._repo.make_repo_path(path)
        with open(_path, "rb") as f:
            pem = f.read()
        self._key = serialization.load_pem_private_key(pem, passphrase, backend=default_backend())
        return self._key

    def check_passphrase(self, path: str, passphrase: bytes=None) -> bool:
        """
        Checks passphrase of a key from repo

        Arguments: path - filename with relative path
                   passphrase - passphrase (must be bytes)
        Returns:   true if passphrase is ok
        """
        _path = self._repo.make_repo_path(path)
        try:
            self.read_private_key(_path, passphrase)
            return True
        except ValueError as e:
            if str(e) == 'Bad decrypt. Incorrect password?':
                return False
            raise e
