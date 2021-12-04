# coding: utf-8
from django.test import TestCase

from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory, UserFactory


class FactoriesTest(TestCase):
    """
    Very simple tests to ensure the factories work as expected.
    """

    def test_user_factory(self):
        user = UserFactory()
        self.assertIsNotNone(user.username)
        self.assertIsNotNone(user.password)
        self.assertIsNotNone(user.first_name)
        self.assertIsNotNone(user.last_name)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_distinguished_name_factory(self):
        dn = DistinguishedNameFactory()
        self.assertIsNotNone(dn.countryName)
        self.assertIsNotNone(dn.stateOrProvinceName)
        self.assertIsNotNone(dn.localityName)
        self.assertIsNotNone(dn.organizationName)
        self.assertIsNotNone(dn.organizationalUnitName)
        self.assertIsNotNone(dn.emailAddress)
        self.assertIsNotNone(dn.commonName)
        self.assertIsNotNone(dn.subjectAltNames)

    def test_certificate_factory(self):
        cert = CertificateFactory()
        self.assertIsNotNone(cert.type)
        self.assertIsNotNone(cert.name)
        self.assertIsNotNone(cert.dn)
        self.assertIsNone(cert.parent)
        self.assertIsNone(cert.crl_distribution_url)
        self.assertIsNone(cert.ocsp_distribution_host)
        self.assertIsNotNone(cert.owner)
        self.assertIsNotNone(cert.serial)
        self.assertIsNotNone(cert.created_at)
        self.assertIsNotNone(cert.expires_at)
        self.assertIsNone(cert.revoked_at)
        self.assertIsNotNone(cert.revoked_uuid)
