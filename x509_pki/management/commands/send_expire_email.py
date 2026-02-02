from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from x509_pki.email_handler import send_mail
from x509_pki.models import Certificate


class Command(BaseCommand):
    help = "Send warning email when certiicate is about to expire"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        max_date = today + timedelta(days=settings.EMAIL_EXPIRATION_WARNING_DAYS)

        certificates = Certificate.objects.filter(
            expires_at__gte=today,
            expires_at__lte=max_date,
            revoked_uuid=0,
            expire_warning_mail_sent_at__isnull=True,
        )

        for cert in certificates:
            ctx = {"cert": cert}
            send_mail("x509_pki/expire_email/expire_warning_mail", cert.owner.email, ctx)
            cert.expire_warning_mail_sent_at = timezone.now()
            cert.save(update_fields=["expire_warning_mail_sent_at"])
