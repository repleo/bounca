from typing import List, Optional, cast

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives.asymmetric.types import CERTIFICATE_PRIVATE_KEY_TYPES
from typing_extensions import get_args


# noinspection PyUnresolvedReferences
class Key(object):
    _key: Optional[CERTIFICATE_PRIVATE_KEY_TYPES] = None

    @property
    def key(self) -> CERTIFICATE_PRIVATE_KEY_TYPES:
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

    def serialize_pkcs12(
        self,
        name: Optional[str] = None,
        certificate: Optional[x509.Certificate] = None,
        passphrase: Optional[str] = None,
        cas: Optional[List[x509.Certificate]] = None,
    ) -> bytes:
        """
        Serialize key

        Arguments: name - Name to use for the supplied certificate and key.
                   certificate - Certificate to contain in pkcs12
                   passphrase - optional passphrase (must be string)
                   cas (list of Certificate or None) – An optional set of certificates to also include in the structure.
        Returns:   bytes
        """

        if not self._key:
            raise RuntimeError("No key object")

        if not isinstance(self._key, get_args(serialization.pkcs12._ALLOWED_PKCS12_TYPES)):
            raise RuntimeError(f"Key object type {type(self._key).__name__} not supported")
        key = cast(serialization.pkcs12._ALLOWED_PKCS12_TYPES, self._key)

        if not name:
            raise ValueError("No name provided")

        if not certificate:
            raise ValueError("No certificate provided")

        encryption = (
            serialization.BestAvailableEncryption(passphrase.encode("utf-8"))
            if passphrase
            else serialization.NoEncryption()
        )
        return serialization.pkcs12.serialize_key_and_certificates(
            name.encode("utf-8"), key, certificate, cas, encryption
        )

    def serialize(
        self, passphrase: Optional[str] = None, encoding: serialization.Encoding = serialization.Encoding.PEM
    ) -> str:
        """
        Serialize key

        Arguments: passphrase - optional passphrase (must be string)
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

    def load(self, pem: str, passphrase: Optional[str] = None) -> "Key":
        """
        Read key from pem

        Arguments: pem - bytes with key
                   passphrase - optional passphrase (must be string)
        Returns:   Self
        """
        try:
            deserialized_key = serialization.load_pem_private_key(
                pem.encode("utf-8"), passphrase.encode("utf-8") if passphrase else None, backend=default_backend()
            )
            self._key = cast(CERTIFICATE_PRIVATE_KEY_TYPES, deserialized_key)
        except ValueError:
            raise ValueError("Bad decrypt. Incorrect password?")
        return self

    @staticmethod
    def check_passphrase(pem: str, passphrase: Optional[str] = None) -> bool:
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
        except TypeError as e:
            if str(e) == "Password was not given but private key is encrypted":
                return False
            raise e
