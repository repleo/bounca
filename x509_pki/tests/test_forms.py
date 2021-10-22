import arrow
from django.test import TestCase
from django.utils import timezone
from unittest import skip

from certificate_engine.types import CertificateTypes
from x509_pki.forms import CertificateForm, DistinguishedNameForm
from x509_pki.models import Certificate, DistinguishedName
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory, UserFactory


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
        self.assertDictEqual(
            form.errors, {'__all__': ['Not allowed to update an existing certificate!']}
        )


class CertificateFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_empty_form(self):
        form = CertificateForm(user=self.user, data={})
        self.assertDictEqual(
            form.errors, {'__all__': ['Non ROOT certificate should have a parent certificate'],
                          'dn': ['This field is required.'],
                          'expires_at': ['This field is required.'],
                          'passphrase_out': ['This field is required.'],
                          'passphrase_out_confirmation': ['This field is required.'],
                          'type': ['This field is required.']
                          }
        )

    def test_empty_with_dn_error(self):
        dn = DistinguishedNameFactory.build()
        form = CertificateForm(user=self.user, data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk
        })
        self.assertDictEqual(
            form.errors,
            {
                'dn': ['This field is required.'],
                'expires_at': ['This field is required.'],
                'passphrase_out': ['This field is required.'],
                'passphrase_out_confirmation': ['This field is required.'],
            }
        )

    @skip("WIP")
    def test_no_update(self):
        crt = CertificateFactory.create(owner=self.user)
        form = CertificateForm(user=self.user, instance=crt, data={
            'type': CertificateTypes.ROOT,
            'dn': crt.dn.pk,
            'expires_at': crt.expires_at,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password'
        })

        self.assertDictEqual(
            form.errors, {'__all__': ['Not allowed to update an existing certificate!']}
        )

    def test_duplicate_name(self):
        CertificateFactory.create(owner=self.user, name="Repleo Root CA")
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'name': "Repleo Root CA",
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password'
        }, user=self.user)

        self.assertDictEqual(
            form.errors, {'__all__': ['name (Repleo Root CA) for Root CA Certificate already exists.']}
        )

    def test_duplicate_dn(self):
        dn = DistinguishedNameFactory(commonName="BounCA CA")
        CertificateFactory.create(owner=self.user, dn=dn)
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'name': "Repleo Root CA",
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password'
        }, user=self.user)

        self.assertDictEqual(
            form.errors, {'__all__': ['DN (BounCA CA) for Root CA Certificate already exists.']}
        )

    def test_minimal_root_form_not_in_future(self):
        dn = DistinguishedNameFactory()
        crt_date = timezone.now().date()

        form = CertificateForm(user=self.user, data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password'
        })
        self.assertDictEqual(
            form.errors, {'expires_at': ['{} is not in the future!'.format(crt_date)]}
        )

    def test_minimal_root_form_passphrase_not_matching(self):
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(user=self.user, data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password_diff'
        })
        self.assertDictEqual(
            form.errors, {'passphrase_out_confirmation': ["The two passphrase fields didn't match."]}
        )

    @skip("FIXME")
    def test_minimal_intermediate_form_passphrase_out_not_valid(self):
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(user=self.user, data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_issuer': 'test_password_invalid',
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password'
        })
        self.assertDictEqual(
            form.errors,
            {'passphrase_issuer':
                ['You should provide a parent certificate if you provide a passphrase in']}
        )

    @skip("FIXME")
    def test_minimal_intermediate_form_passphrase_out_confirmation_not_valid(self):
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(user=self.user, data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_issuer': 'test_password_invalid',
            'passphrase_out': 'test_password_invalid',
            'passphrase_out_confirmation': 'test_password'
        })
        self.assertDictEqual(
            form.errors,
            {'passphrase_issuer':
                ['You should provide a parent certificate if you provide a passphrase in']}
        )

    def test_minimal_root_form_passphrase_issuer_not_allowed(self):
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(user=self.user, data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_issuer': 'test_password',
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password'
        })
        self.assertDictEqual(
            form.errors,
            {'passphrase_issuer':
                ['You should provide a parent certificate if you provide a passphrase in']}
        )

    @skip("WIP")
    def test_minimal_intermediate_form_passphrase_issuer_not_valid(self):
        # TODO WIP
        # dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
        #                               localityName='Amsterdam', organizationName='Repleo',
        #                               organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
        #                               commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        # crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        # form = CertificateForm(user=self.user, data={
        #     'type': CertificateTypes.ROOT,
        #     'dn': dn.pk,
        #     'expires_at': crt_date,
        #     'passphrase_in': 'test_password',
        #     'passphrase_out': 'test_password',
        #     'passphrase_out_confirmation': 'test_password'
        # })
        # self.assertDictEqual(
        #     form.errors, {'passphrase_in': ['You should provide a parent certificate if you provide a passphrase in']}
        # )

        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        crt_root = CertificateFactory.create(owner=self.user, dn=dn,
                                             expires_at=crt_date, type=CertificateTypes.ROOT,
                                             passphrase_out='test_password')
        crt_date = arrow.get(timezone.now()).shift(years=+9).date()
        form = CertificateForm(data={
            'type': CertificateTypes.INTERMEDIATE,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_issuer': 'test_password_invalid',
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'name': 'BounCA INT CA',
            'parent': crt_root,
            'crl_distribution_url': 'https://int.bounca.org/crl/',
            'ocsp_distribution_host': 'https://int.bounca.org/ocsp/',
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {}
        )

    def test_root_form_with_parent(self):
        crt_root = CertificateFactory.create(owner=self.user, type=CertificateTypes.ROOT)
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_root.pk
        }, user=self.user)
        self.assertDictEqual(
            form.errors,
            {'__all__': ['Not allowed to have a parent certificate for a ROOT CA certificate']}
        )

    def test_non_root_form_without_parent(self):
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.INTERMEDIATE,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {'__all__': ['Non ROOT certificate should have a parent certificate']}
        )

    def test_server_form_with_root_parent(self):
        crt_root = CertificateFactory.create(owner=self.user, type=CertificateTypes.ROOT)
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.SERVER_CERT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_root.pk
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {'__all__': ['Server certificate can only be generated for intermediate CA parent']}
        )

    def test_client_form_with_root_parent(self):
        crt_root = CertificateFactory.create(owner=self.user, type=CertificateTypes.ROOT)
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.CLIENT_CERT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_root.pk
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {'__all__': ['Client certificate can only be generated for intermediate CA parent']}
        )

    def assert_duplicate_leaf_certicates(self, type, message):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        crt_root = CertificateFactory.create(owner=self.user, dn=dn, expires_at=crt_date, type=CertificateTypes.ROOT)
        dn_int = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                          localityName='Amsterdam', organizationName='Repleo',
                                          organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                          commonName="int.bounca.org", subjectAltNames=["demo.bounca.org"])
        crt_int = CertificateFactory.create(owner=self.user, dn=dn_int, expires_at=crt_date, parent=crt_root,
                                            type=CertificateTypes.INTERMEDIATE)

        dn_client = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+9).date()
        form = CertificateForm(data={
            'type': type,
            'dn': dn_client.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_int.pk
        }, user=self.user)
        form.save()
        form = CertificateForm(data={
            'type': type,
            'dn': dn_client.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_int.pk
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {'__all__': [message.format(dn_client)]}
        )

    def test_client_duplicate_dn(self):
        self.assert_duplicate_leaf_certicates(CertificateTypes.CLIENT_CERT,
                                              'DN ({}) for Client Certificate already exists.')

    def test_server_duplicate_dn(self):
        self.assert_duplicate_leaf_certicates(CertificateTypes.SERVER_CERT,
                                              'DN ({}) for Server Certificate already exists.')

    def assert_dn_field_not_equal(self, dn_root, dn_intermediate, message):
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        crt_root = CertificateFactory.create(owner=self.user, dn=dn_root,
                                             expires_at=crt_date, type=CertificateTypes.ROOT)
        form = CertificateForm(data={
            'type': CertificateTypes.INTERMEDIATE,
            'dn': dn_intermediate.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_root.pk
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {'__all__': [message]}
        )

    def test_country_not_matching(self):
        dn_root = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                           localityName='Amsterdam', organizationName='Repleo',
                                           organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                           commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_intm = DistinguishedNameFactory(countryName='US', stateOrProvinceName='Noord-Holland',
                                           localityName='Amsterdam', organizationName='Repleo',
                                           organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                           commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        self.assert_dn_field_not_equal(dn_root,
                                       dn_intm,
                                       'Country name of Intermediate CA and Root CA should match (policy strict)')

    def test_state_province_not_matching(self):
        dn_root = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                           localityName='Amsterdam', organizationName='Repleo',
                                           organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                           commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_intm = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Zuid-Holland',
                                           localityName='Amsterdam', organizationName='Repleo',
                                           organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                           commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        self.assert_dn_field_not_equal(dn_root,
                                       dn_intm,
                                       'State Or Province Name of Intermediate CA and Root CA '
                                       'should match (policy strict)')

    def test_organization_not_matching(self):
        dn_root = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                           localityName='Amsterdam', organizationName='Repleo',
                                           organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                           commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_intm = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                           localityName='Amsterdam', organizationName='BounCA',
                                           organizationalUnitName='It Department', emailAddress='info@repleo.nl',
                                           commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        self.assert_dn_field_not_equal(dn_root,
                                       dn_intm,
                                       'Organization Name of Intermediate CA and Root CA should '
                                       'match (policy strict)')

    def test_child_expiration_before_parent(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_int = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                          localityName='Amsterdam', organizationName='Repleo',
                                          organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                          commonName="int.bounca.org", subjectAltNames=["demo.bounca.org"])
        crt_root = CertificateFactory.create(owner=self.user, dn=dn, type=CertificateTypes.ROOT)
        crt_int = CertificateFactory.create(owner=self.user, dn=dn_int,
                                            parent=crt_root, type=CertificateTypes.INTERMEDIATE)

        dn_client = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.CLIENT_CERT,
            'dn': dn_client.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_int.pk
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {'__all__': ['Child Certificate expiration data should be before parent expiration date']}
        )

    def test_crl_distribution_url_has_been_set(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_int = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                          localityName='Amsterdam', organizationName='Repleo',
                                          organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                          commonName="int.bounca.org", subjectAltNames=["demo.bounca.org"])
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        crt_root = CertificateFactory.create(owner=self.user, dn=dn,
                                             expires_at=crt_date, type=CertificateTypes.ROOT)
        form = CertificateForm(data={
            'type': CertificateTypes.INTERMEDIATE,
            'dn': dn_int.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_root.pk
        }, user=self.user)
        form.save()
        o = form.save()
        o = Certificate.objects.get(pk=o.pk)
        self.assertEqual(o.crl_distribution_url, crt_root.crl_distribution_url)
        self.assertEqual(o.ocsp_distribution_host, crt_root.ocsp_distribution_host)

    def test_minimal_root_form(self):
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password'
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {}
        )
        o = form.save()
        o = Certificate.objects.get(pk=o.pk)
        self.assertEqual(o.type, CertificateTypes.ROOT)
        self.assertEqual(o.expires_at, crt_date)
        self.assertEqual(o.dn.pk, dn.pk)
        self.assertEqual(o.passphrase_out, '')
        self.assertEqual(o.passphrase_out_confirmation, '')
        self.assertEqual(o.crl_distribution_url, None)
        self.assertEqual(o.ocsp_distribution_host, None)
        self.assertEqual(o.name, dn.commonName)
        self.assertEqual(o.parent, None)

    def test_full_root_form(self):
        dn = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        form = CertificateForm(data={
            'type': CertificateTypes.ROOT,
            'dn': dn.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'name': 'BounCA ROOT CA',
            'crl_distribution_url': 'https://bounca.org/crl/',
            'ocsp_distribution_host': 'https://bounca.org/ocsp/',
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {}
        )
        o = form.save()
        o = Certificate.objects.get(pk=o.pk)
        self.assertEqual(o.type, CertificateTypes.ROOT)
        self.assertEqual(o.expires_at, crt_date)
        self.assertEqual(o.dn.pk, dn.pk)
        self.assertEqual(o.passphrase_out, '')
        self.assertEqual(o.passphrase_out_confirmation, '')
        self.assertEqual(o.crl_distribution_url, 'https://bounca.org/crl/')
        self.assertEqual(o.ocsp_distribution_host, 'https://bounca.org/ocsp/')
        self.assertEqual(o.name, 'BounCA ROOT CA')
        self.assertEqual(o.parent, None)

    def test_intermediate_form(self):
        dn = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                      localityName='Amsterdam', organizationName='Repleo',
                                      organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                      commonName="test.bounca.org", subjectAltNames=["demo.bounca.org"])
        dn_int = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                          localityName='Amsterdam', organizationName='Repleo',
                                          organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                          commonName="int.bounca.org", subjectAltNames=["demo.bounca.org"])
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        crt_root = CertificateFactory.create(owner=self.user, dn=dn, expires_at=crt_date, type=CertificateTypes.ROOT)
        crt_date = arrow.get(timezone.now()).shift(years=+9).date()
        form = CertificateForm(data={
            'type': CertificateTypes.INTERMEDIATE,
            'dn': dn_int.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'name': 'BounCA INT CA',
            'parent': crt_root,
            'crl_distribution_url': 'https://int.bounca.org/crl/',
            'ocsp_distribution_host': 'https://int.bounca.org/ocsp/',
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {}
        )
        o = form.save()
        o = Certificate.objects.get(pk=o.pk)
        self.assertEqual(o.type, CertificateTypes.INTERMEDIATE)
        self.assertEqual(o.expires_at, crt_date)
        self.assertEqual(o.dn.pk, dn_int.pk)
        self.assertEqual(o.passphrase_out, '')
        self.assertEqual(o.passphrase_out_confirmation, '')
        self.assertEqual(o.crl_distribution_url, 'https://example.com/crl/')
        self.assertEqual(o.ocsp_distribution_host, 'https://example.com/ocsp/')
        self.assertEqual(o.name, 'BounCA INT CA')
        self.assertEqual(o.parent, crt_root)

    def assert_generate_leaf_certificates(self, type):
        dn_root = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                           localityName='Amsterdam', organizationName='Repleo',
                                           organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                           commonName="root ca", subjectAltNames=["demo.bounca.org"])
        crt_date = arrow.get(timezone.now()).shift(years=+10).date()
        crt_root = CertificateFactory.create(owner=self.user, dn=dn_root,
                                             expires_at=crt_date, type=CertificateTypes.ROOT)
        crt_date = arrow.get(timezone.now()).shift(years=+9).date()
        dn_int = DistinguishedNameFactory(countryName='NL', stateOrProvinceName='Noord-Holland',
                                          localityName='Amsterdam', organizationName='Repleo',
                                          organizationalUnitName='IT Department', emailAddress='info@repleo.nl',
                                          commonName="int ca", subjectAltNames=["demo.bounca.org"])
        crt_int = CertificateFactory.create(owner=self.user, dn=dn_int, expires_at=crt_date, parent=crt_root,
                                            type=CertificateTypes.INTERMEDIATE)

        dn_client = DistinguishedNameFactory()
        crt_date = arrow.get(timezone.now()).shift(years=+8).date()
        form = CertificateForm(data={
            'type': type,
            'dn': dn_client.pk,
            'expires_at': crt_date,
            'passphrase_out': 'test_password',
            'passphrase_out_confirmation': 'test_password',
            'parent': crt_int.pk,
            'crl_distribution_url': 'https://crt.bounca.org/crl/',
            'ocsp_distribution_host': 'https://crt.bounca.org/ocsp/',
        }, user=self.user)
        self.assertDictEqual(
            form.errors, {}
        )
        o = form.save()
        o = Certificate.objects.get(pk=o.pk)
        self.assertEqual(o.type, type)
        self.assertEqual(o.expires_at, crt_date)
        self.assertEqual(o.dn.pk, dn_client.pk)
        self.assertEqual(o.passphrase_out, '')
        self.assertEqual(o.passphrase_out_confirmation, '')
        # TODO is this expected behavior? Check with standards. Is it valid to set CRL/OCSP for client certs?
        self.assertEqual(o.crl_distribution_url, 'https://crt.bounca.org/crl/')
        self.assertEqual(o.ocsp_distribution_host, 'https://crt.bounca.org/ocsp/')
        self.assertEqual(o.name, dn_client.commonName)
        self.assertEqual(o.parent, crt_int)
