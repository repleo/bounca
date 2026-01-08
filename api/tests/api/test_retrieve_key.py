from django.db.models.signals import post_save
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.tests.factories import UserFactory
from x509_pki.models import Certificate, generate_certificate
from x509_pki.tests.factories import CertificateFactory, KeyStoreFactory


class CertificateKeyViewTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_get_certificate_key_success(self):
        # ... existing code ...
        # Maak een certificaat met een keystore voor de huidige gebruiker
        cert = CertificateFactory(owner=self.user)
        cert.save()

        url = reverse("certificate-key", kwargs={"pk": cert.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data["text"])
        self.assertTrue("-----BEGIN PRIVATE KEY-----" in response.data["text"])

    def test_get_certificate_key_not_found(self):
        # ... existing code ...
        # Test met een niet-bestaand PK
        url = reverse("certificate-key", kwargs={"pk": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Certificate not found")

    def test_get_certificate_key_unauthorized_owner(self):
        # ... existing code ...
        # Test dat een gebruiker de sleutel van een ander niet kan zien
        other_user = UserFactory()
        cert = CertificateFactory(owner=other_user)
        cert.save()
        KeyStoreFactory(certificate=cert)

        url = reverse("certificate-key", kwargs={"pk": cert.pk})
        response = self.client.get(url)

        # De view filtert op owner, dus geeft 404 als het certificaat van iemand anders is
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_certificate_key_no_keystore(self):
        # ... existing code ...
        # Test scenario waarbij het certificaat bestaat maar geen keystore heeft
        post_save.disconnect(
            receiver=generate_certificate,
            sender=Certificate,
        )
        try:
            cert = CertificateFactory(owner=self.user)
            cert.save()
        # We maken hier expliciet geen keystore aan
        finally:
            post_save.connect(
                receiver=generate_certificate,
                sender=Certificate,
            )

        url = reverse("certificate-key", kwargs={"pk": cert.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Certificate has no keystore", response.data["detail"])
