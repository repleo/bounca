from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creating Site object"

    def add_arguments(self, parser):
        parser.add_argument("host", help="Base host URI of frontend")

    def handle(self, *args, **options):
        print(f"Setting site Frontend URI to: {options['host']}")
        if Site.objects.filter(pk=getattr(settings, "SITE_ID", 1)).exists():
            site = Site.objects.get(pk=getattr(settings, "SITE_ID", 1))
            site.domain = options["host"]
            site.name = getattr(settings, "SITE_NAME", "Bounca PKI")
            site.save()
        else:
            Site(
                pk=getattr(settings, "SITE_ID", 1),
                domain=options["host"],
                name=getattr(settings, "SITE_NAME", "Bounca PKI"),
            ).save()
