from cryptography import x509
from cryptography.x509 import ExtensionOID
from cryptography.x509.oid import NameOID
from django.test import TestCase


class CertificateTestCase(TestCase):

    def assert_subject(self, subject, certificate_request):
        self.assertIsInstance(subject, x509.Name)
        self.assertListEqual(list(subject), [
            x509.NameAttribute(NameOID.COMMON_NAME, certificate_request.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, certificate_request.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, certificate_request.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, certificate_request.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, certificate_request.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, certificate_request.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(certificate_request.dn.countryName)),
        ])

    def assert_crl_distribution(self, crt, certificate_request):
        # crlDistributionspoints
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
        self.assertTrue(ext.critical)
        crl_dp = ext.value
        self.assertEqual(crl_dp[0].full_name[0].value,
                         'URI:{}{}.crl'.format(certificate_request.crl_distribution_url, certificate_request.shortname))
        self.assertEqual(crl_dp[0].reasons,
                         frozenset([
                             x509.ReasonFlags.key_compromise,
                             x509.ReasonFlags.ca_compromise,
                             x509.ReasonFlags.affiliation_changed,
                             x509.ReasonFlags.superseded,
                             x509.ReasonFlags.privilege_withdrawn,
                             x509.ReasonFlags.cessation_of_operation,
                             x509.ReasonFlags.aa_compromise,
                             x509.ReasonFlags.certificate_hold,
                         ]))

    def assert_root_authority(self, crt, certificate_request):
        # keyUsage = basicConstraints = critical, CA:true
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.BasicConstraints(
            ca=True,
            path_length=None
        ))

        # keyUsage = critical, digitalSignature, cRLSign, keyCertSign
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False
        ))
