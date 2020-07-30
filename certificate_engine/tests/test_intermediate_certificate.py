import arrow
# noinspection PyUnresolvedReferences
from cryptography.x509.oid import NameOID
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

    def test_generate_intermediate_certificate_duplicate_commonName(self):
        subject = DistinguishedNameFactory(countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName=self.root_certificate.dn.organizationName,
                                           commonName=self.root_certificate.dn.commonName)
        with self.assertRaises(PolicyError) as context:
            certificate_request = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                                     shortname="test_certificate_duplicate_commonName",
                                                     parent=self.root_certificate, dn=subject,
                                                     key=self.key.serialize())
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request)

        self.assertEqual("CommonName '{}' should not be equal to common "
                         "name of parent".format(self.root_certificate.dn.commonName),
                         str(context.exception))

    def test_generate_intermediate_certificate(self):
        subject = DistinguishedNameFactory(countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName=self.root_certificate.dn.organizationName)

        certificate_request = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                                 shortname="test_generate_intermediate_certificate",
                                                 parent=self.root_certificate, dn=subject,
                                                 key=self.key.serialize())

        certhandler = Certificate()
        certhandler.create_certificate(certificate_request)
        crt = certhandler.certificate

        self.assert_basic_information(crt, certificate_request)

        # subject
        self.assert_subject(crt.subject, certificate_request)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

        # issuer
        self.assert_subject(crt.issuer, self.root_certificate)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

        # crlDistributionspoints
        self.assert_crl_distribution(crt, certificate_request)

        self.assert_intermediate_authority(crt)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        self.assert_oscp(crt, certificate_request)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.root_key, self.root_certificate)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt)

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
