from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.sites.models import Site
from django.test import TestCase, override_settings


class EmailHandlerTests(TestCase):
    @override_settings(DEFAULT_FROM_EMAIL="no-reply@example.com")
    def test_get_from_email_returns_default_from_email_setting(self):
        from x509_pki.email_handler import get_from_email

        self.assertEqual(get_from_email(), "no-reply@example.com")

    @override_settings(SITE_ID=1)
    @patch("x509_pki.email_handler.render_mail")
    @patch("x509_pki.email_handler.get_current_site")
    def test_send_mail_uses_request_context_and_get_current_site(self, get_current_site_mock, render_mail_mock):
        from x509_pki import email_handler

        # Zorg dat er een "global context" is met een request
        req = object()
        email_handler.context = SimpleNamespace(request=req)

        site = MagicMock(spec=Site)
        get_current_site_mock.return_value = site

        msg = MagicMock()
        render_mail_mock.return_value = msg

        email_handler.send_mail(
            template_prefix="x509_pki/expire_email/expire_warning_mail",
            email="user@example.com",
            context={"extra": "value"},
        )

        get_current_site_mock.assert_called_once_with(req)

        render_mail_mock.assert_called_once()
        args, kwargs = render_mail_mock.call_args
        self.assertEqual(args[0], "x509_pki/expire_email/expire_warning_mail")
        self.assertEqual(args[1], "user@example.com")

        merged_ctx = args[2]
        self.assertIs(merged_ctx["request"], req)
        self.assertEqual(merged_ctx["email"], "user@example.com")
        self.assertIs(merged_ctx["current_site"], site)
        self.assertEqual(merged_ctx["extra"], "value")

        msg.send.assert_called_once()

    @override_settings(SITE_ID=123)
    @patch("x509_pki.email_handler.render_mail")
    @patch("x509_pki.email_handler.Site.objects.get")
    def test_send_mail_without_request_falls_back_to_site_by_id(self, site_get_mock, render_mail_mock):
        from x509_pki import email_handler

        # Zorg dat er géén global "context" is
        if "context" in email_handler.__dict__:
            del email_handler.__dict__["context"]

        site = MagicMock(spec=Site)
        site_get_mock.return_value = site

        msg = MagicMock()
        render_mail_mock.return_value = msg

        email_handler.send_mail(
            template_prefix="x509_pki/expire_email/expire_warning_mail",
            email="user@example.com",
            context={"k": "v"},
        )

        site_get_mock.assert_called_once_with(id=123)

        render_mail_mock.assert_called_once()
        args, kwargs = render_mail_mock.call_args
        merged_ctx = args[2]

        self.assertIsNone(merged_ctx["request"])
        self.assertEqual(merged_ctx["email"], "user@example.com")
        self.assertIs(merged_ctx["current_site"], site)
        self.assertEqual(merged_ctx["k"], "v")

        msg.send.assert_called_once()

    @override_settings(SITE_ID=1)
    @patch("x509_pki.email_handler.render_mail")
    @patch("x509_pki.email_handler.Site.objects.get")
    def test_send_mail_context_can_override_defaults(self, site_get_mock, render_mail_mock):
        from x509_pki import email_handler

        if "context" in email_handler.__dict__:
            del email_handler.__dict__["context"]

        site = MagicMock(spec=Site)
        site_get_mock.return_value = site

        msg = MagicMock()
        render_mail_mock.return_value = msg

        # Let op: send_mail doet ctx.update(context), dus context kan keys overschrijven
        email_handler.send_mail(
            template_prefix="tpl",
            email="user@example.com",
            context={"email": "overridden@example.com", "current_site": "OVERRIDE"},
        )

        args, kwargs = render_mail_mock.call_args
        merged_ctx = args[2]

        self.assertEqual(merged_ctx["email"], "overridden@example.com")
        self.assertEqual(merged_ctx["current_site"], "OVERRIDE")
        msg.send.assert_called_once()
