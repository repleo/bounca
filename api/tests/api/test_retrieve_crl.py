from time import sleep

import arrow
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from api.tests.base import APITokenLoginTestCase
from api.tests.factories import AuthorisedAppFactory
from certificate_engine.types import CertificateTypes
from x509_pki.models import Certificate
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory, UserFactory


class CrlRetrieveTest(APITokenLoginTestCase):
    """
    Test retrieving products allowed and not allowed by the current AuthorisedApp Scope
    """

    base_url = "/api/v1/certificates/"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.root_dn = DistinguishedNameFactory(
            countryName="NL",
            stateOrProvinceName="Noord-Holland",
            localityName="Amsterdam",
            organizationName="Repleo",
            organizationalUnitName="IT Department",
            emailAddress="info@repleo.nl",
            commonName="ca.bounca.org",
            subjectAltNames=["demo.bounca.org"],
        )
        cls.user = cls.auth_app.user

        cls.ca = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(years=+10).date(),
            name="repleo root ca",
            type=CertificateTypes.ROOT,
            owner=cls.user,
            passphrase_out="welkom123",
            passphrase_out_confirmation="welkom123",
            dn=cls.root_dn,
            crl_distribution_url="https://example.com/root_ca.crl.pem",
            ocsp_distribution_host="https://example.com/ocsp/",
        )
        cls.ca.save()
        cls.ca.refresh_from_db()
        cls.ca = Certificate.objects.get(pk=cls.ca.pk)

        subject = DistinguishedNameFactory(
            countryName=cls.ca.dn.countryName,
            stateOrProvinceName=cls.ca.dn.stateOrProvinceName,
            organizationName=cls.ca.dn.organizationName,
        )

        cls.int_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
            name="test client intermediate certificate",
            type=CertificateTypes.INTERMEDIATE,
            parent=cls.ca,
            dn=subject,
            passphrase_out="welkom1234",
            passphrase_out_confirmation="welkom1234",
            passphrase_issuer="welkom123",
            crl_distribution_url="https://example.com/crl/cert1.crl.pem",
            ocsp_distribution_host="https://example.com/ocsp/",
        )

        cls.int_certificate.save()

        subject2 = DistinguishedNameFactory(
            countryName=cls.ca.dn.countryName,
            stateOrProvinceName=cls.ca.dn.stateOrProvinceName,
            organizationName=cls.ca.dn.organizationName,
        )

        cls.int_certificate2 = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
            name="test client intermediate certificate2",
            type=CertificateTypes.INTERMEDIATE,
            parent=cls.ca,
            dn=subject2,
            passphrase_out="welkom1235",
            passphrase_out_confirmation="welkom1235",
            passphrase_issuer="welkom123",
            crl_distribution_url="https://example.com/crl/cert2.crl.pem",
            ocsp_distribution_host="https://example.com/ocsp/",
        )

        cls.int_certificate2.save()

    def test_retrieve_crl_root_certificate(self):
        test_uri = f"{self.base_url}{self.ca.pk}/crl"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_crl_root_certificate_last_modified_update(self):
        test_uri = f"{self.base_url}{self.ca.pk}/crl"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ls = response.headers["Last-Modified"]
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Last-Modified"], ls)
        sleep(2)
        client2 = APIClient()
        client2.login(username=self.user.username, password="password123")
        client2.delete(
            f"/api/v1/certificates/{self.int_certificate2.pk}", data={"passphrase_issuer": "welkom123"}, format="json"
        )
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.headers["Last-Modified"], ls)

    def test_retrieve_crl_root_certificate_different_owner(self):
        user = UserFactory.create(username="test_user_diff_crl")
        auth_app = AuthorisedAppFactory(user=user)
        client = self.client_class()
        client.credentials(HTTP_X_AUTH_TOKEN=auth_app.token)
        test_uri = f"{self.base_url}{self.ca.pk}/crl"
        response = client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_root_certificate_token_not_allowed(self):
        test_uri = f"{self.base_url}{self.ca.pk}"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_crl_root_certificate_user_login(self):
        client = APIClient()
        client.login(username=self.user.username, password="password123")
        test_uri = f"{self.base_url}{self.ca.pk}/crl"
        response = client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_root_certificate_user_login(self):
        client = APIClient()
        client.login(username=self.user.username, password="password123")
        test_uri = f"{self.base_url}{self.ca.pk}"
        response = client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
