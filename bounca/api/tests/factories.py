
import factory
from factory.django import DjangoModelFactory
from faker import Factory as FakerFactory
from django.contrib.auth.models import User


fake = FakerFactory.create()


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Faker('email')
    username = factory.Faker('domain_word')
    password = factory.PostGenerationMethodCall('set_password', 'user123')

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    is_superuser = False
    is_staff = False
    is_active = True
