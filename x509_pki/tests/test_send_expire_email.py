# test_send_expire_email_command.py
import datetime
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from x509_pki.models import Certificate
from x509_pki.tests.factories import CertificateFactory


class SendExpireEmailCommandTests(TestCase):
    @override_settings(EXPIRE_WARNING_DAYS=30)
    @patch("x509_pki.management.commands.send_expire_email.send_mail")
    def test_command_sends_mail_and_sets_sent_at_for_expiring_certs(self, send_mail_mock):
        # Arrange: certificaat dat binnen warning-window valt + met email (vaak vereist door de command)
        cert = CertificateFactory(
            expires_at=timezone.now().date() + datetime.timedelta(days=10),
            expire_warning_mail_sent_at=None,
            owner__email="user@example.com",
        )
        cert.save()
        # Act
        call_command("send_expire_email")

        # Assert: mail verstuurd
        self.assertGreaterEqual(send_mail_mock.call_count, 1)

        # Assert: expire_warning_mail_sent_at is gezet
        cert_db = Certificate.objects.filter(pk=cert.pk).first()
        self.assertIsNotNone(cert_db, "Certificate is onverwacht verwijderd door send_expire_email")
        self.assertIsNotNone(cert_db.expire_warning_mail_sent_at)

    @override_settings(EXPIRE_WARNING_DAYS=30)
    @patch("x509_pki.management.commands.send_expire_email.send_mail")
    def test_command_does_not_send_mail_when_already_sent(self, send_mail_mock):
        # Arrange: warning al eerder verstuurd
        cert = CertificateFactory(
            expires_at=timezone.now().date() + datetime.timedelta(days=10),
            expire_warning_mail_sent_at=timezone.now(),
        )
        cert.save()
        # Act
        call_command("send_expire_email")

        # Assert
        send_mail_mock.assert_not_called()

        cert_db = Certificate.objects.filter(pk=cert.pk).first()
        self.assertIsNotNone(cert_db, "Certificate is onverwacht verwijderd door send_expire_email")
        self.assertIsNotNone(cert_db.expire_warning_mail_sent_at)

    @override_settings(EXPIRE_WARNING_DAYS=30)
    @patch("x509_pki.management.commands.send_expire_email.send_mail")
    def test_command_does_not_send_mail_outside_warning_window(self, send_mail_mock):
        # Arrange: nog lang geldig
        cert = CertificateFactory(
            expires_at=timezone.now().date() + datetime.timedelta(days=90),
            expire_warning_mail_sent_at=None,
        )
        cert.save()

        # Act
        call_command("send_expire_email")

        # Assert
        send_mail_mock.assert_not_called()

        cert_db = Certificate.objects.filter(pk=cert.pk).first()
        self.assertIsNotNone(cert_db, "Certificate is onverwacht verwijderd door send_expire_email")
        self.assertIsNone(cert_db.expire_warning_mail_sent_at)

    @override_settings(EXPIRE_WARNING_DAYS=30)
    @patch("x509_pki.management.commands.send_expire_email.send_mail")
    def test_command_is_idempotent_second_run_sends_no_additional_mail(self, send_mail_mock):
        # Arrange
        cert = CertificateFactory(
            expires_at=timezone.now().date() + datetime.timedelta(days=10),
            expire_warning_mail_sent_at=None,
        )
        cert.save()
        # Act: 1e run verstuurt mail
        call_command("send_expire_email")
        first_count = send_mail_mock.call_count

        # Act: 2e run mag niets extra sturen
        call_command("send_expire_email")

        # Assert
        self.assertEqual(send_mail_mock.call_count, first_count)

        cert_db = Certificate.objects.filter(pk=cert.pk).first()
        self.assertIsNotNone(cert_db, "Certificate is onverwacht verwijderd door send_expire_email")
        self.assertIsNotNone(cert_db.expire_warning_mail_sent_at)
