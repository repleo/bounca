from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives.asymmetric.types import PRIVATE_KEY_TYPES


# noinspection PyUnresolvedReferences
class Key(object):
    _key: Optional[PRIVATE_KEY_TYPES] = None

    @property
    def key(self) -> PRIVATE_KEY_TYPES:
        if self._key is None:
            raise RuntimeError("No key object")
        return self._key

    def create_key(self, key_algorithm: str, key_size: int) -> "Key":
        """
        Create a public/private key pair.

        Arguments: key_size - Number of bits to use in the key (only RSA)
                   key_algorithm = the used key algorithm, currently rsa, ed25519 supported
        Returns:   The private key
        """
        if key_algorithm == "ed25519":
            self._key = ed25519.Ed25519PrivateKey.generate()
        elif key_algorithm == "rsa":
            self._key = rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())
        else:
            raise NotImplementedError(f"Key algorithm {key_algorithm} not implemented")
        return self

    def serialize(self, passphrase: str = None, encoding: serialization.Encoding = serialization.Encoding.PEM) -> str:
        """
        Serialize key

        Arguments: path - filename with relative path
                   passphrase - optional passphrase (must be bytes)
                   encoding - optional different encoding
        Returns:   string
        """

        if not self._key:
            raise RuntimeError("No key object")

        encryption = (
            serialization.BestAvailableEncryption(passphrase.encode("utf-8"))
            if passphrase
            else serialization.NoEncryption()
        )
        return self._key.private_bytes(
            encoding=encoding,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption,
        ).decode("utf-8")

    def load(self, pem: str, passphrase: str = None) -> "Key":
        """
        Read key from pem

        Arguments: pem - bytes with key
                   passphrase - optional passphrase (must be string)
        Returns:   Self
        """
        self._key = serialization.load_pem_private_key(
            pem.encode("utf-8"), passphrase.encode("utf-8") if passphrase else None, backend=default_backend()
        )
        return self

    @staticmethod
    def check_passphrase(pem: str, passphrase: str = None) -> bool:
        """
        Checks passphrase of a pem key file

        Arguments: pem - string with key
                   passphrase - passphrase (must be string)
        Returns:   true if passphrase is ok
        """
        try:
            serialization.load_pem_private_key(
                pem.encode("utf-8"), passphrase.encode("utf-8") if passphrase else None, backend=default_backend()
            )
            return True
        except ValueError as e:
            if str(e) == "Bad decrypt. Incorrect password?":
                return False
            raise e
