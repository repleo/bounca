import arrow
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from api.tests.base import APITokenLoginTestCase
from api.tests.factories import AuthorisedAppFactory
from certificate_engine.types import CertificateTypes
from x509_pki.models import Certificate
from x509_pki.tests.factories import DistinguishedNameFactory, UserFactory


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

        cls.ca = Certificate()
        cls.ca.type = CertificateTypes.ROOT
        cls.ca.name = "repleo root ca"
        cls.ca.crl_distribution_url = "https://example.com/root_ca.crl.pem"
        cls.ca.dn = cls.root_dn
        cls.ca.expires_at = arrow.get(timezone.now()).shift(years=+10).date()

        cls.ca.revoked_at = None
        cls.ca.owner = cls.user
        cls.ca.save()

        cls.ca.refresh_from_db()
        cls.ca = Certificate.objects.get(pk=cls.ca.pk)

    def test_retrieve_crl_root_certificate(self):
        test_uri = f"{self.base_url}{self.ca.pk}/crl"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
