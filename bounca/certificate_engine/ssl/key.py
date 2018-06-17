
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey


class Key(object):

    def __init__(self) -> None:
        self._key = None  # type: RSAPrivateKey

    @property
    def key(self) -> RSAPrivateKey:
        return self._key

    def create_key(self, key_size: int) -> 'Key':
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
        return self

    def serialize(self, passphrase: bytes=None, encoding: str=serialization.Encoding.PEM) -> bytes:
        """
        Serialize key

        Arguments: path - filename with relative path
                   passphrase - optional passphrase (must be bytes)
                   encoding - optional different encoding
        Returns:   bytes
        """

        if not self._key:
            raise RuntimeError("No key object")

        encryption = serialization.BestAvailableEncryption(passphrase) if passphrase else serialization.NoEncryption()
        return self._key.private_bytes(
            encoding=encoding,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption,
        )

    def load(self, pem: bytes, passphrase: bytes=None) -> RSAPrivateKey:
        """
        Read key from pem

        Arguments: pem - bytes with key
                   passphrase - optional passphrase (must be bytes)
        Returns:   Self
        """
        self._key = serialization.load_pem_private_key(pem, passphrase, backend=default_backend())
        return self

    def check_passphrase(self, pem: bytes, passphrase: bytes=None) -> bool:
        """
        Checks passphrase of a pem key file

        Arguments: pem - bytes with key
                   passphrase - passphrase (must be bytes)
        Returns:   true if passphrase is ok
        """
        try:
            serialization.load_pem_private_key(pem, passphrase, backend=default_backend())
            return True
        except ValueError as e:
            if str(e) == 'Bad decrypt. Incorrect password?':
                return False
            raise e
