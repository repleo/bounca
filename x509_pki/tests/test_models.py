# coding: utf-8
import arrow
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.test import TestCase
from django.utils import timezone
from unittest import skip
from uuid import UUID

from certificate_engine.types import CertificateTypes
from x509_pki.models import Certificate, DistinguishedName
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory, UserFactory


class ModelDistinguishedNameTest(TestCase):
    def test_distinguished_name_to_dn(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        self.assertEqual(dn.dn, "CN=test.bounca.org, O=Repleo, OU=IT Department, L=Amsterdam, ST=Noord-Holland, "
                                "EMAIL=info@repleo.nl, C=NL")
        self.assertEqual(dn.subj, "/CN=test.bounca.org/O=Repleo/OU=IT Department/L=Amsterdam/ST=Noord-Holland"
                                  "/emailAddress=info@repleo.nl/C=NL")
        self.assertEqual(dn.countryName, "NL")
        self.assertEqual(dn.stateOrProvinceName, "Noord-Holland")
        self.assertEqual(dn.localityName, "Amsterdam")
        self.assertEqual(dn.organizationName, "Repleo")
        self.assertEqual(dn.organizationalUnitName, "IT Department")
        self.assertEqual(dn.emailAddress, "info@repleo.nl")
        self.assertEqual(dn.commonName, "test.bounca.org")
        self.assertEqual(dn.subjectAltNames, ["demo.bounca.org"])
        self.assertEqual(dn.slug_commonName, "testbouncaorg")

    def test_distinguished_name_update_not_allowed(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn = DistinguishedName.objects.get(id=dn.id)
        dn.commonName = "www.bounca.org"
        with self.assertRaises(ValidationError) as c:
            dn.save()
        self.assertEqual(c.exception.message,
                         'Not allowed to update a DistinguishedName record')

    def test_distinguished_name_validation_in_future_not_allowed(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn = DistinguishedName.objects.get(id=dn.id)
        dn.commonName = "www.bounca.org"
        with self.assertRaises(ValidationError) as c:
            dn.save()
        self.assertEqual(c.exception.message,
                         'Not allowed to update a DistinguishedName record')


class ModelCertificateTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.root_dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                               localityName='Amsterdam', organizationName='Repleo',
                                               organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                               commonName="ca.bounca.org", subjectAltNames=["demo.bounca.org"])
        cls.user = UserFactory()

        cls.ca = Certificate()
        cls.ca.type = CertificateTypes.ROOT
        cls.ca.name = "repleo root ca"
        cls.ca.dn = cls.root_dn
        cls.ca.crl_distribution_url = "https://ca.demo.repleo.nl/crl/test.crl.pem"
        cls.ca.ocsp_distribution_host = "https://ca.demo.repleo.nl/ocsp"
        cls.ca.expires_at = arrow.get(timezone.now()).shift(years=+10).date()

        cls.ca.revoked_at = None
        cls.ca.owner = cls.user
        cls.ca.save()

        cls.ca.refresh_from_db()
        cls.ca = Certificate.objects.get(pk=cls.ca.pk)
        cls.int_dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                              localityName='Amsterdam', organizationName='Repleo',
                                              organizationalUnitName='IT Department',
                                              emailAddress='info@repleo.nl',
                                              commonName="int.bounca.org",
                                              subjectAltNames=["demo.bounca.org"])
        cls.int = Certificate(parent=cls.ca)
        cls.int.type = CertificateTypes.INTERMEDIATE
        cls.int.name = "repleo int ca"
        cls.int.dn = cls.int_dn
        cls.int.crl_distribution_url = "https://ca.demo.repleo.nl/crl/test.crl.pem"
        cls.int.ocsp_distribution_host = "https://ca.demo.repleo.nl/ocsp"
        cls.int.expires_at = arrow.get(timezone.now()).shift(years=+5).date()

        cls.int.revoked_at = None
        cls.int.owner = cls.user
        cls.int.save()
        cls.int.refresh_from_db()

    def test_generate_root_certificate(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department',
                                      emailAddress='info@repleo.nl',
                                      commonName="test bounca org",
                                      subjectAltNames=["demo.bounca.org"])
        cert = Certificate()
        cert.type = CertificateTypes.ROOT
        cert.name = "repleo root ca1"
        cert.dn = dn
        cert.crl_distribution_url = "https://ca.demo.repleo.nl/crl/test.crl.pem"
        cert.ocsp_distribution_host = "https://ca.demo.repleo.nl/ocsp"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+10).date()

        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()

        self.assertEqual(cert.dn.dn, "CN=test bounca org, O=Repleo, OU=IT Department, "
                                     "L=Amsterdam, ST=Noord-Holland, EMAIL=info@repleo.nl, C=NL")
        self.assertEqual(cert.type, CertificateTypes.ROOT)
        self.assertEqual(cert.name, "repleo root ca1")
        self.assertEqual(cert.crl_distribution_url, "https://ca.demo.repleo.nl/crl/test.crl.pem")
        self.assertEqual(cert.ocsp_distribution_host, "https://ca.demo.repleo.nl/ocsp")
        self.assertEqual(cert.created_at, arrow.get(cert.expires_at).shift(years=-10).date())
        self.assertEqual(cert.expires_at, arrow.get(cert.created_at).shift(years=+10).date())
        self.assertIsNone(cert.revoked_at)
        self.assertEqual(cert.owner, self.user)
        self.assertEqual(cert.revoked_uuid, UUID(int=0))
        self.assertNotEqual(cert.serial, 0)
        self.assertIsNone(cert.slug_revoked_at)
        self.assertFalse(cert.revoked)
        self.assertFalse(cert.expired)
        self.assertEqual(cert.slug_name, "repleo-root-ca1")

        self.assertIsNotNone(cert.crlstore.crl)

    def test_generate_intermediate_certificate(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        cert = Certificate(parent=self.ca)
        cert.type = CertificateTypes.INTERMEDIATE
        cert.name = "repleo int ca1"
        cert.dn = dn
        cert.crl_distribution_url = "https://ca.demo.repleo.nl/crl/test.crl.pem"
        cert.ocsp_distribution_host = "https://ca.demo.repleo.nl/ocsp"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+5).date()

        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()

        self.assertEqual(cert.dn.dn, "CN=test.bounca.org, O=Repleo, OU=IT Department, "
                                     "L=Amsterdam, ST=Noord-Holland, EMAIL=info@repleo.nl, C=NL")
        self.assertEqual(cert.type, CertificateTypes.INTERMEDIATE)
        self.assertEqual(cert.name, "repleo int ca1")
        self.assertEqual(cert.crl_distribution_url, "https://ca.demo.repleo.nl/crl/test.crl.pem")
        self.assertEqual(cert.ocsp_distribution_host, "https://ca.demo.repleo.nl/ocsp")
        self.assertEqual(cert.created_at, arrow.get(cert.expires_at).shift(years=-5).date())
        self.assertEqual(cert.expires_at, arrow.get(cert.created_at).shift(years=+5).date())
        self.assertIsNone(cert.revoked_at)
        self.assertEqual(cert.owner, self.user)
        self.assertEqual(cert.revoked_uuid, UUID(int=0))
        self.assertNotEqual(cert.serial, 0)
        self.assertIsNone(cert.slug_revoked_at)
        self.assertFalse(cert.revoked)
        self.assertFalse(cert.expired)

        self.assertIsNotNone(cert.crlstore.crl)

    def test_generate_server_certificate(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="www.repleo.nl", subjectAltNames=["repleo.nl"])

        cert = Certificate(parent=self.int, dn=dn)
        cert.type = CertificateTypes.SERVER_CERT
        cert.name = "www.repleo.nl"
        cert.dn = dn
        cert.crl_distribution_url = "https://ca.demo.repleo.nl/crl/test.crl.pem"
        cert.ocsp_distribution_host = "https://ca.demo.repleo.nl/ocsp"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+1).date()

        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()

        self.assertEqual(cert.dn.dn, "CN=www.repleo.nl, O=Repleo, OU=IT Department, "
                                     "L=Amsterdam, ST=Noord-Holland, EMAIL=info@repleo.nl, C=NL")
        self.assertEqual(cert.type, CertificateTypes.SERVER_CERT)
        self.assertEqual(cert.name, "www.repleo.nl")
        self.assertEqual(cert.crl_distribution_url, "https://ca.demo.repleo.nl/crl/test.crl.pem")
        self.assertEqual(cert.ocsp_distribution_host, "https://ca.demo.repleo.nl/ocsp")
        self.assertEqual(cert.created_at, arrow.get(cert.expires_at).shift(years=-1).date())
        self.assertEqual(cert.expires_at, arrow.get(cert.created_at).shift(years=+1).date())
        self.assertIsNone(cert.revoked_at)
        self.assertEqual(cert.owner, self.user)
        self.assertEqual(cert.revoked_uuid, UUID(int=0))
        self.assertNotEqual(cert.serial, 0)
        self.assertIsNone(cert.slug_revoked_at)
        self.assertFalse(cert.revoked)
        self.assertFalse(cert.expired)

        with self.assertRaises(ObjectDoesNotExist) as c:
            cert.crlstore
        self.assertEqual(str(c.exception),
                         'Certificate has no crlstore.')

        cert.delete()
        cert.refresh_from_db()
        self.assertIsNotNone(cert.revoked_at)
        self.assertIsNotNone(cert.slug_revoked_at)
        self.assertNotEqual(cert.revoked_uuid, UUID(int=0))

    def test_generate_client_certificate(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="info@bounca.org")

        cert = Certificate(parent=self.int, dn=dn)
        cert.type = CertificateTypes.CLIENT_CERT
        cert.name = "info@bounca.org"
        cert.dn = dn
        cert.crl_distribution_url = "https://ca.demo.repleo.nl/crl/test.crl.pem"
        cert.ocsp_distribution_host = "https://ca.demo.repleo.nl/ocsp"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+1).date()

        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()

        self.assertEqual(cert.dn.dn, "CN=info@bounca.org, O=Repleo, OU=IT Department, "
                                     "L=Amsterdam, ST=Noord-Holland, EMAIL=info@repleo.nl, C=NL")
        self.assertEqual(cert.type, CertificateTypes.CLIENT_CERT)
        self.assertEqual(cert.name, "info@bounca.org")
        self.assertEqual(cert.crl_distribution_url, "https://ca.demo.repleo.nl/crl/test.crl.pem")
        self.assertEqual(cert.ocsp_distribution_host, "https://ca.demo.repleo.nl/ocsp")
        self.assertEqual(cert.created_at, arrow.get(cert.expires_at).shift(years=-1).date())
        self.assertEqual(cert.expires_at, arrow.get(cert.created_at).shift(years=+1).date())
        self.assertIsNone(cert.revoked_at)
        self.assertEqual(cert.owner, self.user)
        self.assertEqual(cert.revoked_uuid, UUID(int=0))
        self.assertNotEqual(cert.serial, 0)
        self.assertIsNone(cert.slug_revoked_at)
        self.assertFalse(cert.revoked)
        self.assertFalse(cert.expired)

        with self.assertRaises(ObjectDoesNotExist) as c:
            cert.crlstore
        self.assertEqual(str(c.exception),
                         'Certificate has no crlstore.')

        cert.delete()
        cert.refresh_from_db()
        self.assertIsNotNone(cert.revoked_at)
        self.assertIsNotNone(cert.slug_revoked_at)
        self.assertNotEqual(cert.revoked_uuid, UUID(int=0))

    @skip("TODO check if values are valid")
    def test_generate_ocsp_certificate(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="ca.demo.repleo.nl")

        cert = Certificate(parent=self.int, dn=dn)
        cert.type = CertificateTypes.OCSP
        cert.name = "ca.demo.repleo.nl"
        cert.dn = dn
        cert.crl_distribution_url = "https://ca.demo.repleo.nl/crl/"
        cert.ocsp_distribution_host = "https://ca.demo.repleo.nl/ocsp"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+1).date()

        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()

        self.assertEqual(cert.dn.dn, "CN=https://ca.demo.repleo.nl/ocsp, O=Repleo, OU=IT Department, "
                                     "L=Amsterdam, ST=Noord-Holland, EMAIL=info@repleo.nl, C=NL")
        self.assertEqual(cert.type, CertificateTypes.OCSP)
        self.assertEqual(cert.name, "https://ca.demo.repleo.nl/ocsp")
        self.assertEqual(cert.crl_distribution_url, "https://ca.demo.repleo.nl/crl/")
        self.assertEqual(cert.ocsp_distribution_host, "https://ca.demo.repleo.nl/ocsp")
        self.assertEqual(cert.created_at, arrow.get(cert.expires_at).shift(years=-1).date())
        self.assertEqual(cert.expires_at, arrow.get(cert.created_at).shift(years=+1).date())
        self.assertIsNone(cert.revoked_at)
        self.assertEqual(cert.owner, self.user)
        self.assertEqual(cert.revoked_uuid, UUID(int=0))
        self.assertNotEqual(cert.serial, 0)
        self.assertIsNone(cert.slug_revoked_at)
        self.assertFalse(cert.revoked)
        self.assertFalse(cert.expired)

        with self.assertRaises(ValidationError) as c:
            cert.generate_crl()
        self.assertEqual(c.exception.message,
                         'CRL File can only be generated for Intermediate Certificates')

        # TODO test revocation/delete

    def test_days_valid(self):
        dn_ca = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        cert = CertificateFactory(dn=dn_ca, type=CertificateTypes.ROOT)
        cert.expires_at = arrow.get(timezone.now()).shift(years=+10).date()
        self.assertEqual(cert.days_valid, 3652)
        cert.save()
        cert.refresh_from_db()
        self.assertEqual(cert.days_valid, 3652)

    def test_set_name_to_common_name(self):
        dn_ca = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        cert = CertificateFactory(name="", dn=dn_ca, type=CertificateTypes.ROOT)
        cert.save()
        cert.refresh_from_db()
        self.assertEqual(cert.name, cert.dn.commonName)
        self.assertEqual(cert.slug_name, "testbouncaorg")

    def test_generate_root_certificate_unique_violate_name(self):
        cert = CertificateFactory()
        cert.type = CertificateTypes.ROOT
        cert.name = "repleo root ca 1"
        cert.save()
        cert = CertificateFactory()
        cert.type = CertificateTypes.ROOT
        cert.name = "repleo root ca 1"
        with self.assertRaises(ValidationError):
            cert.save()

    def test_generate_root_certificate_unique_violate_dn(self):
        dn_ca = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        cert = CertificateFactory()
        cert.dn = dn_ca
        cert.type = CertificateTypes.ROOT
        cert.name = "repleo root ca 1"
        cert.save()
        cert = CertificateFactory()
        cert.dn = dn_ca
        cert.type = CertificateTypes.ROOT
        cert.name = "repleo root ca 2"
        with self.assertRaises(ValidationError):
            cert.save()

    def test_parent_not_allowed_for_root_certificate(self):
        ca = CertificateFactory(type=CertificateTypes.ROOT)
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.ROOT, parent=ca)
        cert.type = CertificateTypes.ROOT
        cert.name = "repleo root ca 1"
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message, 'Not allowed to have a parent certificate for a Root CA certificate')

    def test_parent_intermediate_has_no_root_parent(self):
        cert = CertificateFactory(type=CertificateTypes.INTERMEDIATE)
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message, 'Non Root certificate should have a parent')

    def test_client_cert_parent_no_intermediate_parent(self):
        ca = CertificateFactory(type=CertificateTypes.ROOT)
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.CLIENT_CERT, parent=ca)
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message, 'Client certificate can only be generated for intermediate CA parent')

    def test_server_cert_parent_no_intermediate_parent(self):
        ca = CertificateFactory(type=CertificateTypes.ROOT)
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.SERVER_CERT, parent=ca)
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message, 'Server certificate can only be generated for intermediate CA parent')

    def test_ocsp_cert_parent_no_intermediate_parent(self):
        ca = CertificateFactory(type=CertificateTypes.ROOT)
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.OCSP, parent=ca)
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message, 'OCSP certificate can only be generated for intermediate CA parent')

    def test_ocsp_cert_parent_is_not_intermediate_parent(self):
        ca = CertificateFactory(type=CertificateTypes.ROOT)
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.OCSP, parent=ca)
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message, 'OCSP certificate can only be generated for intermediate CA parent')

    def test_intermediate_dn_country_difference(self):
        dn_ca = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_im = DistinguishedNameFactory(countryName='IT', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        ca = CertificateFactory(type=CertificateTypes.ROOT, dn=dn_ca)
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.INTERMEDIATE, parent=ca, dn=dn_im)
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message,
                         'Country name of Intermediate CA and Root CA should match (policy strict)')

    def test_intermediate_dn_state_difference(self):
        dn_ca = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_im = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Zuid-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        ca = CertificateFactory(type=CertificateTypes.ROOT, dn=dn_ca)
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.INTERMEDIATE, parent=ca, dn=dn_im)
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message,
                         'State Or Province Name of Intermediate CA and Root CA should match (policy strict)')

    def test_intermediate_dn_organization_difference(self):
        dn_ca = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_im = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='BJA Electronics',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        ca = CertificateFactory(type=CertificateTypes.ROOT, dn=dn_ca)
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.INTERMEDIATE, parent=ca, dn=dn_im)
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message,
                         'Organization Name of Intermediate CA and Root CA should match (policy strict)')

    def test_child_expire_date_exceeds_parent_expire_date(self):
        dn_ca = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_im = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                         localityName='Amsterdam', organizationName='Repleo',
                                         organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                         commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        ca = CertificateFactory(type=CertificateTypes.ROOT, dn=dn_ca)
        ca.expires_at = arrow.get(timezone.now()).shift(years=+10).date()
        ca.save()
        cert = CertificateFactory(type=CertificateTypes.INTERMEDIATE, parent=ca, dn=dn_im)
        cert.expires_at = arrow.get(timezone.now()).shift(years=+20).date()
        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message,
                         'Child Certificate (expire date: {}) should not '
                         'expire later than parent CA (expire date: {})'.format(cert.expires_at, ca.expires_at))

    def test_passphrase_out_not_matching(self):
        cert = CertificateFactory(type=CertificateTypes.ROOT)
        cert.passphrase_out = "test"
        cert.passphrase_out_confirmation = "test2"

        with self.assertRaises(ValidationError) as c:
            cert.save()
        self.assertEqual(c.exception.message, "The two passphrase fields didn't match.")
