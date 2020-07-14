import random

import arrow
import factory
from django.contrib.auth.models import User
from django.db.models import signals
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Factory as FakerFactory

from bounca.x509_pki.models import Certificate, DistinguishedName
from bounca.x509_pki.types import CertificateTypes


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
    subjectAltNames = [factory.Faker('domain_name') for x in range(random.randint(0, 5))]


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class CertificateFactory(DjangoModelFactory):

    class Meta:
        model = Certificate

    type = CertificateTypes.ROOT
    shortname = fake.word()
    name = fake.sentence(nb_words=6, variable_nb_words=True)
    dn = factory.LazyFunction(DistinguishedNameFactory)
    parent = None
    crl_distribution_url = 'https://example.com/crl/'
    ocsp_distribution_host = 'https://example.com/ocsp/'
    owner = factory.LazyFunction(UserFactory)

    created_at = factory.LazyFunction(lambda: arrow.get(timezone.now()).date())
    expires_at = factory.LazyFunction(lambda: arrow.get(timezone.now()).replace(days=+1).date())
    revoked_at = None
    revoked_uuid = '00000000000000000000000000000001'
    key = b""
    crt = b""
