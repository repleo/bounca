# noinspection PyUnresolvedReferences
from cryptography.x509.oid import NameOID


class CertificateTypes(object):
    ROOT = "R"
    INTERMEDIATE = "I"
    SERVER_CERT = "S"
    CLIENT_CERT = "C"
    OCSP = "O"


class CertificatePolicy(object):
    policy = {
        'supplied': [
            ('commonName', NameOID.COMMON_NAME),
        ],
        'match': [
        ],
        'optional': [
            ('countryName', NameOID.COUNTRY_NAME),
            ('stateOrProvinceName', NameOID.STATE_OR_PROVINCE_NAME),
            ('localityName', NameOID.LOCALITY_NAME),
            ('organizationName', NameOID.ORGANIZATION_NAME),
            ('organizationalUnitName', NameOID.ORGANIZATIONAL_UNIT_NAME),
            ('emailAddress', NameOID.EMAIL_ADDRESS),
        ]
    }


class CertificateRootPolicy(CertificatePolicy):
    # The root CA should have all fields which are required to sign intermediate certificates.
    policy = {
        'supplied': [
            ('countryName', NameOID.COUNTRY_NAME),
            ('stateOrProvinceName', NameOID.STATE_OR_PROVINCE_NAME),
            ('organizationName', NameOID.ORGANIZATION_NAME),
            ('commonName', NameOID.COMMON_NAME)
        ],
        'match': [
        ],
        'optional': [
            ('organizationalUnitName', NameOID.ORGANIZATIONAL_UNIT_NAME),
            ('emailAddress', NameOID.EMAIL_ADDRESS)
        ]
    }


class CertificateIntermediatePolicy(CertificatePolicy):
    # The root CA should only sign intermediate certificates that match.
    policy = {
        'supplied': [
            ('commonName', NameOID.COMMON_NAME),
        ],
        'match': [
            ('countryName', NameOID.COUNTRY_NAME),
            ('stateOrProvinceName', NameOID.STATE_OR_PROVINCE_NAME),
            ('organizationName', NameOID.ORGANIZATION_NAME)
        ],
        'optional': [
            ('organizationalUnitName', NameOID.ORGANIZATIONAL_UNIT_NAME),
            ('emailAddress', NameOID.EMAIL_ADDRESS)
        ]
    }
