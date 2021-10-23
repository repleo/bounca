import arrow
import factory
import random
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from factory import BUILD_STRATEGY
from factory.django import DjangoModelFactory
from faker import Factory as FakerFactory

from certificate_engine.types import CertificateTypes
from x509_pki.models import Certificate, DistinguishedName


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

    @classmethod
    def default(cls):
        try:
            user = User.objects.get(username='jeroen')
        except ObjectDoesNotExist:
            user = UserFactory.create(username='jeroen')
        return user


class DistinguishedNameFactory(DjangoModelFactory):

    class Meta:
        model = DistinguishedName

    countryName = factory.Faker('country_code')
    stateOrProvinceName = factory.Faker('state')
    localityName = factory.Faker('city')
    organizationName = factory.Faker('company')
    organizationalUnitName = fake.sentence(nb_words=3, variable_nb_words=True)
    emailAddress = factory.Faker('email')
    commonName = factory.Faker('domain_name')
    subjectAltNames = factory.List([
        factory.Faker('domain_name') for _ in range(random.randint(1, 5))
    ])


class CertificateFactory(DjangoModelFactory):

    class Meta:
        model = Certificate
        strategy = BUILD_STRATEGY

    type = CertificateTypes.ROOT
    name = fake.sentence(nb_words=6, variable_nb_words=True)
    dn = factory.LazyFunction(DistinguishedNameFactory)
    parent = None
    crl_distribution_url = 'https://example.com/crl/cert.crl.pem'
    ocsp_distribution_host = 'https://example.com/ocsp/'
    owner = factory.LazyFunction(UserFactory.default)

    created_at = factory.LazyFunction(lambda: arrow.get(timezone.now()).date())
    expires_at = factory.LazyFunction(lambda: arrow.get(timezone.now()).shift(days=+1).date())
    revoked_at = None
