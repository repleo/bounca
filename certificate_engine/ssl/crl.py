import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed448, ed25519
from cryptography.x509 import CertificateRevocationList, RevokedCertificate
from cryptography.x509.oid import NameOID
from typing import List, Tuple

from certificate_engine.ssl.certificate import PassPhraseError
from certificate_engine.ssl.key import Key


def revocation_builder(pem: str, timestamp: datetime.datetime) -> RevokedCertificate:
    certificate = x509.load_pem_x509_certificate(pem.encode('utf8'), backend=default_backend())
    revoked_cert = x509.RevokedCertificateBuilder().serial_number(
        certificate.serial_number
    ).revocation_date(
        timestamp
    ).build()
    return revoked_cert


def revocation_list_builder(certificates: List[Tuple[str, datetime.datetime]],
                            ca: str, key: str, passphrase: str = None,
                            last_update: datetime.datetime = None,
                            next_update: datetime.datetime = None) \
        -> CertificateRevocationList:
    """
    Create certificate revocation list

    Arguments: certificates - The certificates in tuples with revocation date
               ca - The authority certificate (pem bytes)
               key - The authority private key (pem bytes)
               passphrase - The passphrase of the key of the certificate
    Returns:   The certificate revocation list object
    """
    try:
        ca_key = Key().load(key, passphrase)
    except ValueError:
        raise PassPhraseError("Bad passphrase, could not decode private key")

    one_day = datetime.timedelta(1, 0, 0)

    builder = x509.CertificateRevocationListBuilder()
    ca_crt = x509.load_pem_x509_certificate(ca.encode('utf8'), backend=default_backend())
    common_name_attrs = ca_crt.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if len(common_name_attrs) != 1:
        raise ValueError("CommonName has not been set")
    common_name = common_name_attrs[0].value
    builder = builder.issuer_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ]))
    last_update = datetime.datetime.today() if not last_update else last_update
    next_update = datetime.datetime.today() + one_day if not next_update else next_update

    builder = builder.last_update(last_update)
    builder = builder.next_update(next_update)

    for pem, timestamp in certificates:
        revoked_cert = revocation_builder(pem, timestamp)
        builder = builder.add_revoked_certificate(revoked_cert)

    algorithm = None if isinstance(
        ca_key.key, (ed25519.Ed25519PrivateKey, ed448.Ed448PrivateKey)
    ) else hashes.SHA256()
    crl = builder.sign(
        private_key=ca_key.key, algorithm=algorithm,
    )
    return crl


def serialize(crl: CertificateRevocationList,
              encoding: serialization.Encoding = serialization.Encoding.PEM) -> str:
    """
    Serialize CertificateRevocationList

    Arguments: crl - the certificatelist, encoding - optional different encoding
    Returns:   bytes
    """
    if crl is None:
        raise RuntimeError("No certificate revocation list object")

    if encoding not in serialization.Encoding:
        raise ValueError("{} is not a valid encoding")

    return crl.public_bytes(encoding=encoding).decode('utf8')
