from django.test import TestCase

from x509_pki.forms import DistinguishedNameForm
from x509_pki.models import DistinguishedName
from x509_pki.tests.factories import DistinguishedNameFactory


class DistinguishedNameFormTest(TestCase):
    def test_empty_form(self):
        form = DistinguishedNameForm(data={})

        self.assertEqual(
            form.errors, {'commonName': ['This field is required.']}
        )

    def test_minimal_form(self):
        form = DistinguishedNameForm(data={'commonName': 'ca.repleo.nl'})

        self.assertEqual(
            form.errors, {}
        )
        o = form.save()
        o = DistinguishedName.objects.get(pk=o.pk)
        self.assertEqual(o.commonName, 'ca.repleo.nl')

    def test_full_form(self):
        dn = DistinguishedNameFactory.build()

        form = DistinguishedNameForm(data={
            'commonName': dn.commonName,
            'countryName': dn.countryName,
            'stateOrProvinceName': dn.stateOrProvinceName,
            'localityName': dn.localityName,
            'organizationName': dn.organizationName,
            'organizationalUnitName': dn.organizationalUnitName,
            'emailAddress': dn.emailAddress,
            'subjectAltNames': dn.subjectAltNames})

        self.assertEqual(
            form.errors, {}
        )
        o = form.save()
        o = DistinguishedName.objects.get(pk=o.pk)
        self.assertEqual(o.commonName, dn.commonName)
        self.assertEqual(o.countryName, dn.countryName)
        self.assertEqual(o.stateOrProvinceName, dn.stateOrProvinceName)
        self.assertEqual(o.localityName, dn.localityName)
        self.assertEqual(o.organizationName, dn.organizationName)
        self.assertEqual(o.organizationalUnitName, dn.organizationalUnitName)
        self.assertEqual(o.emailAddress, dn.emailAddress)
        self.assertEqual(o.subjectAltNames, dn.subjectAltNames)

    def test_no_update(self):
        dn = DistinguishedNameFactory()

        form = DistinguishedNameForm(instance=dn, data={'commonName': 'ca.repleo.nl'})
        self.assertEqual(
            form.errors, {'__all__': ['Not allowed to update an existing certificate!']}
        )

