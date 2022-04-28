# noinspection PyUnresolvedReferences
from abc import ABC

from cryptography.x509.oid import NameOID


class CertificateTypes(object):
    ROOT = "R"
    INTERMEDIATE = "I"
    SERVER_CERT = "S"
    CLIENT_CERT = "C"
    OCSP = "O"


class CertificateBasePolicy(ABC):
    fields_dn: list = [
        ("countryName", NameOID.COUNTRY_NAME),
        ("stateOrProvinceName", NameOID.STATE_OR_PROVINCE_NAME),
        ("localityName", NameOID.LOCALITY_NAME),
        ("organizationName", NameOID.ORGANIZATION_NAME),
        ("organizationalUnitName", NameOID.ORGANIZATIONAL_UNIT_NAME),
        ("commonName", NameOID.COMMON_NAME),
        ("emailAddress", NameOID.EMAIL_ADDRESS),
    ]
    policy: dict = {}


class CertificatePolicy(CertificateBasePolicy):
    fields_dn: list = [
        ("countryName", NameOID.COUNTRY_NAME),
        ("stateOrProvinceName", NameOID.STATE_OR_PROVINCE_NAME),
        ("localityName", NameOID.LOCALITY_NAME),
        ("organizationName", NameOID.ORGANIZATION_NAME),
        ("organizationalUnitName", NameOID.ORGANIZATIONAL_UNIT_NAME),
        ("commonName", NameOID.COMMON_NAME),
        ("emailAddress", NameOID.EMAIL_ADDRESS),
        ("subjectAltNames", None),
    ]
    policy: dict = {
        "supplied": [
            "commonName",
            "subjectAltNames",
        ],
        "match": [],
        "optional": [
            "countryName",
            "stateOrProvinceName",
            "localityName",
            "organizationName",
            "organizationalUnitName",
            "emailAddress",
        ],
    }


class CertificateRootPolicy(CertificateBasePolicy):
    # The root CA should have all fields which are required to sign intermediate certificates.
    policy: dict = {
        "supplied": [
            "countryName",
            "stateOrProvinceName",
            "organizationName",
            "commonName",
        ],
        "match": [],
        "optional": [
            "organizationalUnitName",
            "localityName",
            "emailAddress",
        ],
    }


class CertificateIntermediatePolicy(CertificateBasePolicy):
    # The root CA should only sign intermediate certificates that match.
    policy: dict = {
        "supplied": ["commonName"],
        "match": [
            "countryName",
            "stateOrProvinceName",
            "organizationName",
        ],
        "optional": [
            "organizationalUnitName",
            "localityName",
            "emailAddress",
        ],
    }
