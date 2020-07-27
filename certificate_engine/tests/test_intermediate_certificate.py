# coding: utf-8
import arrow
import datetime
from cryptography import x509
from cryptography.x509 import ExtensionOID
from cryptography.x509.extensions import _key_identifier_from_public_key
from cryptography.x509.oid import AuthorityInformationAccessOID, NameOID
from django.utils import timezone

from certificate_engine.ssl.certificate import Certificate, PassPhraseError, PolicyError
from certificate_engine.ssl.key import Key
from certificate_engine.tests.helpers import CertificateTestCase
from certificate_engine.types import CertificateTypes
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class IntermediateCertificateTest(CertificateTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_key = Key().create_key(4096)
        subject = DistinguishedNameFactory(countryName='NL',
                                           stateOrProvinceName='Noord Holland',
                                           organizationName='Repleo')

        cls.root_certificate = CertificateFactory(dn=subject,
                                                  expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                                  key=cls.root_key.serialize())
        certificate = Certificate()
        certificate.create_certificate(cls.root_certificate)

        cls.root_certificate.crt = certificate.serialize()
        cls.root_certificate.save()
        cls.key = Key().create_key(4096)

    def test_parent_not_set(self):
        subject = DistinguishedNameFactory(countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName=self.root_certificate.dn.organizationName,
                                           localityName=self.root_certificate.dn.localityName)
        certificate = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                         shortname="test_parent_object_not_set",
                                         parent=None, dn=subject,
                                         key=self.key.serialize())
        with self.assertRaises(RuntimeError) as context:
            certhandler = Certificate()
            certhandler.create_certificate(certificate)
        self.assertEqual("Parent certificate is required", str(context.exception))

    def test_parent_object_not_set(self):
        subject = DistinguishedNameFactory(countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName=self.root_certificate.dn.organizationName,
                                           localityName=self.root_certificate.dn.localityName)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                              shortname="root_test_parent_object_not_set",
                                              key=self.root_key.serialize())
        certificate = Certificate()
        certificate.create_certificate(root_certificate)

        key = Key().create_key(2048)
        certificate = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                         shortname="test_parent_object_not_set",
                                         parent=root_certificate, dn=subject,
                                         key=key.serialize())
        with self.assertRaises(RuntimeError) as context:
            certhandler = Certificate()
            certhandler.create_certificate(certificate)
        self.assertEqual("Parent certificate object has not been set", str(context.exception))

    def root_ca_not_matching_attribute(self, subject, attribute_name):
        with self.assertRaises(PolicyError) as context:
            certificate_request = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                                     shortname="root_ca_not_matching_attribute",
                                                     parent=self.root_certificate, dn=subject,
                                                     key=self.key.serialize())
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request)

        self.assertEqual("Certificate should match field '{}' "
                         "(issuer certificate: {}, certificate: {})"
                         .format(attribute_name, getattr(self.root_certificate.dn, attribute_name),
                                 getattr(subject, attribute_name)),
                         str(context.exception))

    def test_generate_intermediate_certificate_not_matching_countryName(self):
        subject = DistinguishedNameFactory(countryName='DE',
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName=self.root_certificate.dn.organizationName)
        self.root_ca_not_matching_attribute(subject, 'countryName')

    def test_generate_intermediate_certificate_not_matching_stateOrProvinceName(self):
        subject = DistinguishedNameFactory(countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName='Utrecht',
                                           organizationName=self.root_certificate.dn.organizationName)
        self.root_ca_not_matching_attribute(subject, 'stateOrProvinceName')

    def test_generate_intermediate_certificate_not_matching_organizationName(self):
        subject = DistinguishedNameFactory(countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName='BJA Electronics')
        self.root_ca_not_matching_attribute(subject, 'organizationName')

    def test_generate_intermediate_certificate(self):
        key = Key().create_key(4096)

        subject = DistinguishedNameFactory(countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName=self.root_certificate.dn.organizationName)

        certificate_request = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                                 shortname="test_generate_intermediate_certificate",
                                                 parent=self.root_certificate, dn=subject,
                                                 key=key.serialize())

        certhandler = Certificate()
        certhandler.create_certificate(certificate_request)
        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate_request.created_at.year,
            month=certificate_request.created_at.month,
            day=certificate_request.created_at.day
        ))

        self.assertEqual(crt.not_valid_after, datetime.datetime(
            year=certificate_request.expires_at.year,
            month=certificate_request.expires_at.month,
            day=certificate_request.expires_at.day
        ))

        # subject
        self.assert_subject(crt.subject, certificate_request)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

        # issuer
        self.assert_subject(crt.issuer, self.root_certificate)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

        # crlDistributionspoints
        self.assert_crl_distribution(crt, certificate_request)

        # keyUsage = basicConstraints = critical, CA:true
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.BasicConstraints(
            ca=True,
            path_length=0
        ))

        # keyUsage = critical, digitalSignature, cRLSign, keyCertSign
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False
        ))

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value[0], x509.AccessDescription(
            AuthorityInformationAccessOID.OCSP,
            x509.UniformResourceIdentifier(certificate_request.ocsp_distribution_host)
        ))

        # authorityKeyIdentifier = keyid:always, issuer
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(self.root_key.key.public_key()))
        self.assertEqual(ext.value.authority_cert_serial_number, int(self.root_certificate.serial))
        self.assertEqual([x.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value for x in
                          ext.value.authority_cert_issuer[0].value.rdns if
                          x.get_attributes_for_oid(NameOID.COMMON_NAME)][0],
                         str(self.root_certificate.dn))

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(key.key.public_key()))

    def test_generate_intermediate_certificate_minimal(self):
        key = Key().create_key(4096)

        subject = DistinguishedNameFactory(organizationalUnitName=None,
                                           emailAddress=None,
                                           localityName=None,
                                           countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName=self.root_certificate.dn.organizationName)

        certificate_request = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                                 shortname="test_generate_intermediate_certificate_minimal",
                                                 parent=self.root_certificate, dn=subject,
                                                 key=key.serialize())

        certhandler = Certificate()
        certhandler.create_certificate(certificate_request)
        crt = certhandler.certificate
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())

        # subject
        self.assert_subject(crt.subject, certificate_request)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

        # issuer
        self.assert_subject(crt.issuer, self.root_certificate)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

    def test_generate_intermediate_certificate_passphrase(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                              shortname="root_test_generate_intermediate_certificate_passphrase",
                                              key=root_key.serialize(passphrase=b'SecretRootPP'))
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate, passphrase=b'SecretRootPP')
        root_certificate.crt = root_certhandler.serialize()
        root_certificate.save()

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName,
                                           localityName=root_certificate.dn.localityName)

        certificate_request = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                                 shortname="test_generate_intermediate_certificate_passphrase",
                                                 parent=root_certificate, dn=subject,
                                                 key=self.key.serialize(passphrase=b'SecretPP'))
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, passphrase=b'SecretPP', passphrase_issuer=b'SecretRootPP')

        crt = certhandler.certificate
        # subject
        self.assert_subject(crt.subject, certificate_request)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

        # issuer
        self.assert_subject(crt.issuer, root_certificate)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

    def test_generate_intermediate_certificate_passphrase_wrong_cert_passphrase(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                              shortname="root_test_certificate_passphrase_wrong_cert_passphrase",
                                              key=root_key.serialize(passphrase=b'SecretRootPP'))
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate, passphrase=b'SecretRootPP')

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName)

        certificate = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                         shortname="test_certificate_passphrase_wrong_cert_passphrase",
                                         parent=root_certificate, dn=subject,
                                         key=self.key.serialize(passphrase=b'SecretPP'))
        certhandler = Certificate()
        with self.assertRaisesMessage(PassPhraseError, "Bad passphrase, could not decode private key"):
            certhandler.create_certificate(certificate,
                                           passphrase=b'SecretPPInvalid',
                                           passphrase_issuer=b'SecretRootPP')

    def test_generate_intermediate_certificate_passphrase_wrong_issuer_passphrase(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                              shortname="root_test_certificate_passphrase_wrong_issuer_passphrase",
                                              key=root_key.serialize(passphrase=b'SecretRootPP'))
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate, passphrase=b'SecretRootPP')

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName)

        certificate = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                         shortname="test_certificate_passphrase_wrong_issuer_passphrase",
                                         parent=root_certificate, dn=subject,
                                         key=self.key.serialize(passphrase=b'SecretPP'))
        certhandler = Certificate()
        with self.assertRaisesMessage(PassPhraseError, "Bad passphrase, could not decode issuer key"):
            certhandler.create_certificate(certificate,
                                           passphrase=b'SecretPP',
                                           passphrase_issuer=b'SecretRootPPInvalid')
