from rest_framework.test import APITestCase

from api.tests.factories import AuthorisedAppFactory


class APITokenLoginTestCase(APITestCase):
    """
    APITestCase that uses our AuthorisedApp model token to login.
    """

    @classmethod
    def setUpTestData(cls):
        cls.auth_app = AuthorisedAppFactory()

    def setUp(self):
        self.client.credentials(HTTP_X_AUTH_TOKEN=self.auth_app.token)


class APILoginTestCase(APITestCase):
    """
    APITestCase that uses credentials to login.
    """

    @classmethod
    def setUpTestData(cls):
        cls.auth_app = AuthorisedAppFactory()
        cls.user = cls.auth_app.user

    def setUp(self):
        self.client.login(username=self.user.username, password="password123")

    def assertCertInResponseList(self, response, certificate, msg=None):
        self.assertTrue(response.data)
        self.assertEqual([r['dn']['commonName'] for r in response.data if r['name'] == certificate.name],
                         [certificate.dn.commonName], msg=msg)

    def assertCertNotInResponseList(self, response, certificate, msg=None):
        self.assertTrue(response.data)
        self.assertListEqual([r['dn']['commonName'] for r in response.data if r['name'] == certificate.name],
                         [], msg=msg)
