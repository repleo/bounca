from dj_rest_auth.models import TokenModel
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Set email verification flag"

    def add_arguments(self, parser):
        parser.add_argument("email", help="Email of the account")

    def handle(self, *args, **options):
        if User.objects.filter(email=options['email']).exists():
            print(f"Set email verification flag of: {options['email']}")
            user = User.objects.get(email=options['email'])
            token_model = TokenModel.objects.get_or_create(user=user)

            user.email_verified = True
            user.save()
        else:
            print(f"User with email {options['email']} does not exist")
