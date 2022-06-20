import factory
from django.core.exceptions import ObjectDoesNotExist
from factory.django import DjangoModelFactory
from faker import Factory as FakerFactory

from api import models, utils
from x509_pki.tests.factories import UserFactory

fake = FakerFactory.create()


class AuthorisedAppFactory(DjangoModelFactory):
    class Meta:
        model = models.AuthorisedApp

    name = fake.sentence(nb_words=6, variable_nb_words=True)
    token = factory.LazyFunction(utils.new_token)
    user = factory.LazyFunction(UserFactory.default)

    @classmethod
    def default(cls):
        try:
            authorised_app = models.AuthorisedApp.objects.get(token="aasdfghjkl")
        except ObjectDoesNotExist:
            authorised_app = AuthorisedAppFactory.create(token="aasdfghjkl")
        return authorised_app
