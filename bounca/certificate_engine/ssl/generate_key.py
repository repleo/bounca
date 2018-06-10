from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


def createKey(key_size):
    """
    Create a public/private key pair.

    Arguments: key_size - Number of bits to use in the key
    Returns:   The private key
    """
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    return key
