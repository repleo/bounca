import datetime

from cryptography import x509
from cryptography.x509 import ExtensionOID

# noinspection PyProtectedMember,PyUnresolvedReferences
from cryptography.x509.extensions import _key_identifier_from_public_key

# noinspection PyUnresolvedReferences
from cryptography.x509.oid import AuthorityInformationAccessOID, NameOID
from django.test import TestCase


class CertificateTestCase(TestCase):
    def assert_subject(self, subject, certificate_request):
        self.assertIsInstance(subject, x509.Name)
        self.assertIn(x509.NameAttribute(NameOID.COMMON_NAME, certificate_request.dn.commonName), subject)
        nr_of_attributes = 0
        for attr in [
            (NameOID.COUNTRY_NAME, "countryName"),
            (NameOID.STATE_OR_PROVINCE_NAME, "stateOrProvinceName"),
            (NameOID.LOCALITY_NAME, "localityName"),
            (NameOID.ORGANIZATION_NAME, "organizationName"),
            (NameOID.ORGANIZATIONAL_UNIT_NAME, "organizationalUnitName"),
            (NameOID.EMAIL_ADDRESS, "emailAddress"),
            (NameOID.COMMON_NAME, "commonName"),
        ]:
            a = (
                getattr(certificate_request.dn, attr[1]).code
                if attr[1] == "countryName"
                else getattr(certificate_request.dn, attr[1])
            )
            if a:
                self.assertIn(x509.NameAttribute(attr[0], a), subject)
                nr_of_attributes += 1
        self.assertEqual(len(subject), nr_of_attributes)

    def assert_crl_distribution(self, crt, certificate_request):
        # crlDistributionspoints
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
        self.assertTrue(ext.critical)
        crl_dp = ext.value
        self.assertEqual(crl_dp[0].full_name[0].value, certificate_request.crl_distribution_url)
        self.assertEqual(
            crl_dp[0].reasons,
            frozenset(
                [
                    x509.ReasonFlags.key_compromise,
                    x509.ReasonFlags.ca_compromise,
                    x509.ReasonFlags.affiliation_changed,
                    x509.ReasonFlags.superseded,
                    x509.ReasonFlags.privilege_withdrawn,
                    x509.ReasonFlags.cessation_of_operation,
                    x509.ReasonFlags.aa_compromise,
                    x509.ReasonFlags.certificate_hold,
                ]
            ),
        )

    def assert_root_authority(self, crt, path_length=None):
        # keyUsage = basicConstraints = critical, CA:true
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.BasicConstraints(ca=True, path_length=path_length))

        # keyUsage = critical, digitalSignature, cRLSign, keyCertSign
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        self.assertTrue(ext.critical)
        self.assertEqual(
            ext.value,
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
        )

    def assert_user_certificate(self, crt, content_commitment=False):
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        self.assertFalse(ext.critical)
        self.assertEqual(ext.value, x509.BasicConstraints(ca=False, path_length=None))

        ext = crt.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        self.assertTrue(ext.critical)
        self.assertEqual(
            ext.value,
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=content_commitment,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
        )

    def assert_ocsp_certificate(self, crt):
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        self.assertFalse(ext.critical)
        self.assertEqual(ext.value, x509.BasicConstraints(ca=False, path_length=None))

        ext = crt.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        self.assertTrue(ext.critical)
        self.assertEqual(
            ext.value,
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
        )

    def assert_intermediate_authority(self, crt, path_length=0):
        self.assert_root_authority(crt, path_length=path_length)

    def assert_basic_information(self, crt, certificate):
        self.assertEqual(crt.serial_number, int(certificate.serial))
        # noinspection PyUnresolvedReferences
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())
        self.assertEqual(
            crt.not_valid_before,
            datetime.datetime(
                year=certificate.created_at.year, month=certificate.created_at.month, day=certificate.created_at.day
            ),
        )

        self.assertEqual(
            crt.not_valid_after,
            datetime.datetime(
                year=certificate.expires_at.year, month=certificate.expires_at.month, day=certificate.expires_at.day
            ),
        )

    def assert_hash(self, crt):
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        # noinspection PyUnresolvedReferences
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(self.key.key.public_key()))

    def assert_oscp(self, crt, certificate):
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        self.assertTrue(ext.critical)
        self.assertEqual(
            ext.value[0],
            x509.AccessDescription(
                AuthorityInformationAccessOID.OCSP, x509.UniformResourceIdentifier(certificate.ocsp_distribution_host)
            ),
        )

    def assert_authority_key(self, crt, key, issuer_certificate=None):
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(key.key.public_key()))
        if issuer_certificate:
            self.assertEqual(ext.value.authority_cert_serial_number, int(issuer_certificate.serial))

            self.assertEqual(
                [
                    x.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                    for x in ext.value.authority_cert_issuer[0].value.rdns
                    if x.get_attributes_for_oid(NameOID.COMMON_NAME)
                ][0],
                str(issuer_certificate.dn.commonName),
            )

    def assert_extension(self, crt, oid, value, critical=False):
        ext = crt.extensions.get_extension_for_oid(oid)
        self.assertEqual(ext.critical, critical)
        self.assertEqual([x for x in ext.value], value)
