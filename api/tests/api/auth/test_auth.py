from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class AuthRegistrationTest(APITestCase):
    """
    Test retrieve and creating tokens
    """

    base_url = "/api/v1/reqistration"

    def test_account_email_verification_sent_not_found(self):
        client = APIClient()
        response = client.get(f"{self.base_url}/account-email-verification-sent/", format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
