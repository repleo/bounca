from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from api.models import AuthorisedApp
from api.tests.factories import AuthorisedAppFactory
from x509_pki.tests.factories import UserFactory


class TokensTest(APITestCase):
    """
    Test retrieve and creating tokens
    """

    base_url = "/api/v1/"
    test_uri = f"{base_url}auth/tokens/"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = UserFactory.default()
        cls.client = APIClient()
        cls.alt_user = UserFactory.create(username="test_user_diff_crl")

    def setUp(self):
        self.client.login(username=self.user.username, password="password123")

    def test_retrieve_tokens_anonymous(self):
        client = APIClient()
        response = client.get(self.test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_tokens_no(self):
        response = self.client.get(self.test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_retrieve_tokens_one(self):
        token_1 = AuthorisedAppFactory(name="token_1", user=self.user)
        response = self.client.get(self.test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], token_1.name)

    def test_retrieve_tokens_one_of_two(self):
        token_1a = AuthorisedAppFactory(name="token_1a", user=self.user)
        AuthorisedAppFactory(name="token_1b", user=self.alt_user)
        response = self.client.get(self.test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], token_1a.name)

    def test_retrieve_tokens_two(self):
        token_1 = AuthorisedAppFactory(name="token_1", user=self.user)
        token_2 = AuthorisedAppFactory(name="token_2", user=self.user)
        AuthorisedAppFactory(name="token_1", user=self.alt_user)
        response = self.client.get(self.test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], token_1.name)
        self.assertEqual(response.data[1]["name"], token_2.name)

    def test_create_token(self):
        response = self.client.post(self.test_uri, {"name": "token_1_api"}, format="json")
        self.assertEqual(response.data["name"], "token_1_api")
        self.assertTrue(bool(response.data["token"]))
        response = self.client.get(self.test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "token_1_api")

    def test_create_token_invalid(self):
        response = self.client.post(self.test_uri, {}, format="json")
        self.assertEqual(response.data["name"], [ErrorDetail(string="This field is required.", code="required")])

    def test_create_token_ignore_token(self):
        response = self.client.post(self.test_uri, {"name": "token_1_api", "token": "bogus"}, format="json")
        self.assertTrue(bool(response.data["token"]))
        self.assertNotEqual(response.data["token"], "bogus")

    def test_create_token_ignore_user(self):
        response = self.client.post(self.test_uri, {"name": "token_1_api", "user": self.alt_user.pk}, format="json")
        self.assertTrue(bool(response.data["token"]))
        self.assertEqual(response.data["user"], self.user.id)

    def test_create_token_double_name(self):
        self.client.post(self.test_uri, {"name": "token_1_api"}, format="json")
        response = self.client.post(self.test_uri, {"name": "token_1_api"}, format="json")
        self.assertDictEqual(
            response.data,
            {
                "non_field_errors": [
                    ErrorDetail(string="The fields name, user " "must make a unique set.", code="unique")
                ]
            },
        )

    def test_retrieve_token(self):
        token_1 = AuthorisedAppFactory(name="token_1_retrieve", user=self.user)
        retrieve_uri = f"{self.test_uri}{token_1.id}/"
        response = self.client.get(retrieve_uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "token_1_retrieve")
        self.assertIsNotNone(AuthorisedApp.objects.get(pk=token_1.id))

    def test_delete_token(self):
        token_1 = AuthorisedAppFactory(name="token_1_retrieve", user=self.user)
        retrieve_uri = f"{self.test_uri}{token_1.id}/"
        response = self.client.get(retrieve_uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "token_1_retrieve")
        response = self.client.delete(retrieve_uri)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertListEqual(list(AuthorisedApp.objects.filter(pk=token_1.id)), [])

    def test_delete_token_not_owned(self):
        token_1 = AuthorisedAppFactory(name="token_1_retrieve", user=self.alt_user)
        retrieve_uri = f"{self.test_uri}{token_1.id}/"
        response = self.client.get(retrieve_uri)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(retrieve_uri)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(AuthorisedApp.objects.get(pk=token_1.id))
