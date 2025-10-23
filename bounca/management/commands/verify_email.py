from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

class Command(BaseCommand):
    help = "Set email verification flag"

    def add_arguments(self, parser):
        parser.add_argument("email", help="Email of the account")

    def handle(self, *args, **options):
        if User.objects.filter(email=options['email']).exists():
            print(f"Set email verification flag of: {options['email']}")
            user = User.objects.get(email=options['email'])
            email, created = EmailAddress.objects.get_or_create(user=user, email=options['email'])
            email.verified = True
            email.save()
            print(f"User email verified: {email}")
        else:
            print(f"User with email {options['email']} does not exist")
