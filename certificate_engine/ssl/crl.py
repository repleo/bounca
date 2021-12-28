import datetime
from typing import TYPE_CHECKING, List, Tuple

import pytz
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed448, ed25519
from cryptography.x509 import CertificateRevocationList, RevokedCertificate

from certificate_engine.ssl.certificate import Certificate, PassPhraseError
from certificate_engine.ssl.key import Key

if TYPE_CHECKING:
    from x509_pki.models import Certificate as CertificateType
else:
    CertificateType = object


def revocation_builder(pem: str, timestamp: datetime.datetime) -> RevokedCertificate:
    certificate = x509.load_pem_x509_certificate(pem.encode("utf8"), backend=default_backend())
    revoked_cert = (
        x509.RevokedCertificateBuilder().serial_number(certificate.serial_number).revocation_date(timestamp).build()
    )
    return revoked_cert


def revocation_list_builder(
    certificates: List[Tuple[str, datetime.datetime]],
    issuer_cert: CertificateType,
    passphrase: str = None,
    last_update: datetime.datetime = None,
    next_update: datetime.datetime = None,
) -> CertificateRevocationList:
    """
    Create certificate revocation list

    Arguments: certificates - The certificates in tuples with revocation date
               ca - The authority certificate (pem bytes)
               key - The authority private key (pem bytes)
               passphrase - The passphrase of the key of the certificate
    Returns:   The certificate revocation list object
    """
    try:
        ca_key = Key().load(issuer_cert.keystore.key, passphrase)
    except ValueError:
        raise PassPhraseError("Bad passphrase, could not decode private key")

    one_day = datetime.timedelta(1, 0, 0)

    builder = x509.CertificateRevocationListBuilder()
    builder = builder.issuer_name(Certificate.build_subject_names(issuer_cert))
    last_update = datetime.datetime.now(tz=pytz.UTC) if not last_update else last_update
    next_update = datetime.datetime.now(tz=pytz.UTC) + one_day if not next_update else next_update

    builder = builder.last_update(last_update)
    builder = builder.next_update(next_update)

    for pem, timestamp in certificates:
        revoked_cert = revocation_builder(pem, timestamp)
        builder = builder.add_revoked_certificate(revoked_cert)

    algorithm = None if isinstance(ca_key.key, (ed25519.Ed25519PrivateKey, ed448.Ed448PrivateKey)) else hashes.SHA256()
    crl = builder.sign(
        private_key=ca_key.key,
        algorithm=algorithm,
    )
    return crl


def serialize(crl: CertificateRevocationList, encoding: serialization.Encoding = serialization.Encoding.PEM) -> str:
    """
    Serialize CertificateRevocationList

    Arguments: crl - the certificatelist, encoding - optional different encoding
    Returns:   bytes
    """
    if crl is None:
        raise RuntimeError("No certificate revocation list object")

    if encoding not in serialization.Encoding:
        raise ValueError("{} is not a valid encoding")

    return crl.public_bytes(encoding=encoding).decode("utf8")
