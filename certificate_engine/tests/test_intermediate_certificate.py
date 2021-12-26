import arrow

# noinspection PyUnresolvedReferences
from cryptography.x509.oid import NameOID
from django.db.models import signals
from django.utils import timezone
from factory.django import mute_signals

from certificate_engine.ssl.certificate import Certificate, PassPhraseError, PolicyError
from certificate_engine.ssl.key import Key
from certificate_engine.tests.helpers import CertificateTestCase
from certificate_engine.types import CertificateTypes
from x509_pki.models import KeyStore
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class IntermediateCertificateTest(CertificateTestCase):
    @classmethod
    def setUpTestData(cls):
        with mute_signals(signals.post_save):
            cls.root_key = Key().create_key("rsa", 4096)
            subject = DistinguishedNameFactory(
                countryName="NL", stateOrProvinceName="Noord Holland", organizationName="Repleo"
            )

            cls.root_certificate = CertificateFactory(
                dn=subject, expires_at=arrow.get(timezone.now()).shift(days=+3).date()
            )
            cls.root_certificate.save()
            certificate = Certificate()
            key = cls.root_key.serialize()
            certificate.create_certificate(cls.root_certificate, key)
            keystore = KeyStore(certificate=cls.root_certificate)
            keystore.crt = certificate.serialize()
            keystore.key = key
            keystore.save()
            cls.key = Key().create_key("rsa", 4096)

    def test_parent_not_set(self):
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
            localityName=self.root_certificate.dn.localityName,
        )
        certificate = CertificateFactory(
            type=CertificateTypes.INTERMEDIATE, name="test_parent_object_not_set", parent=None, dn=subject
        )
        with self.assertRaises(RuntimeError) as context:
            certhandler = Certificate()
            certhandler.create_certificate(certificate, self.key.serialize())
        self.assertEqual("Parent certificate is required", str(context.exception))

    def test_parent_object_not_set(self):
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
            localityName=self.root_certificate.dn.localityName,
            commonName="ca test repleo",
        )
        root_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
            name="root_test_parent_object_not_set",
            dn=subject,
        )
        with mute_signals(signals.post_save):
            root_certificate.save()
        certificate = Certificate()
        certificate.create_certificate(root_certificate, self.root_key.serialize())

        keystore = KeyStore(certificate=root_certificate)
        keystore.crt = ""
        keystore.key = self.root_key.serialize()
        keystore.save(full_clean=False)

        key = Key().create_key("ed25519", None)
        subject_int = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
            localityName=self.root_certificate.dn.localityName,
            commonName="ca int test repleo",
        )
        certificate = CertificateFactory(
            type=CertificateTypes.INTERMEDIATE,
            name="test_parent_object_not_set",
            parent=root_certificate,
            dn=subject_int,
        )
        with self.assertRaises(RuntimeError) as context:
            certhandler = Certificate()
            certhandler.create_certificate(certificate, key.serialize())
        self.assertEqual("Parent certificate object has not been set", str(context.exception))

    def root_ca_not_matching_attribute(self, subject, attribute_name):
        with self.assertRaises(PolicyError) as context:
            certificate_request = CertificateFactory(
                type=CertificateTypes.INTERMEDIATE,
                name="root_ca_not_matching_attribute",
                parent=self.root_certificate,
                dn=subject,
            )
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request, self.key.serialize())

        self.assertEqual(
            "Certificate should match field '{}' "
            "(issuer certificate: {}, certificate: {})".format(
                attribute_name, getattr(self.root_certificate.dn, attribute_name), getattr(subject, attribute_name)
            ),
            str(context.exception),
        )

    def test_generate_intermediate_certificate_not_matching_countryName(self):
        subject = DistinguishedNameFactory(
            countryName="DE",
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
        )
        self.root_ca_not_matching_attribute(subject, "countryName")

    def test_generate_intermediate_certificate_not_matching_stateOrProvinceName(self):
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName="Utrecht",
            organizationName=self.root_certificate.dn.organizationName,
        )
        self.root_ca_not_matching_attribute(subject, "stateOrProvinceName")

    def test_generate_intermediate_certificate_not_matching_organizationName(self):
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName="BJA Electronics",
        )
        self.root_ca_not_matching_attribute(subject, "organizationName")

    def test_generate_intermediate_certificate_duplicate_commonName(self):
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
            commonName=self.root_certificate.dn.commonName,
        )
        with self.assertRaises(PolicyError) as context:
            certificate_request = CertificateFactory(
                type=CertificateTypes.INTERMEDIATE,
                name="test_certificate_duplicate_commonName",
                parent=self.root_certificate,
                dn=subject,
            )
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request, self.key.serialize())

        self.assertEqual(
            "CommonName '{}' should not be equal to common "
            "name of parent".format(self.root_certificate.dn.commonName),
            str(context.exception),
        )

    def test_generate_intermediate_certificate(self):
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
            localityName="Amsterdam",
        )

        certificate_request = CertificateFactory(
            type=CertificateTypes.INTERMEDIATE,
            name="test_generate_intermediate_certificate",
            parent=self.root_certificate,
            dn=subject,
            crl_distribution_url="https://example.com/crl/cert.crl.pem",
            ocsp_distribution_host="https://example.com/ocsp/",
        )
        certificate_request.save()
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, self.key.serialize())
        crt = certhandler.certificate

        self.assert_basic_information(crt, certificate_request)

        # subject
        self.assert_subject(crt.subject, certificate_request)
        self.assertEqual("Amsterdam", crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value)

        # issuer
        self.assert_subject(crt.issuer, self.root_certificate)
        self.assertEqual("Amsterdam", crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value)

        self.assert_intermediate_authority(crt)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.root_key, None, critical=False)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt)

        # crlDistributionspoints
        self.assert_crl_distribution(crt, self.root_certificate)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        self.assert_oscp(crt, self.root_certificate)

    def test_generate_intermediate_certificate_minimal(self):
        key = Key().create_key("rsa", 4096)

        subject = DistinguishedNameFactory(
            organizationalUnitName=None,
            emailAddress=None,
            localityName=None,
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
        )

        certificate_request = CertificateFactory(
            type=CertificateTypes.INTERMEDIATE,
            name="test_generate_intermediate_certificate_minimal",
            parent=self.root_certificate,
            dn=subject,
        )
        certificate_request.save()
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, key.serialize())
        crt = certhandler.certificate
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())

        # subject
        self.assert_subject(crt.subject, certificate_request)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

        # issuer
        self.assert_subject(crt.issuer, self.root_certificate)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))

    def test_generate_intermediate_certificate_passphrase(self):
        root_key = Key().create_key("ed25519", None)
        root_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
            name="root_test_generate_intermediate_certificate_passphrase",
        )
        with mute_signals(signals.post_save):
            root_certificate.save()
        root_certhandler = Certificate()
        root_certhandler.create_certificate(
            root_certificate, root_key.serialize(passphrase="SecretRootPP"), passphrase="SecretRootPP"
        )
        keystore = KeyStore(certificate=root_certificate)
        keystore.crt = root_certhandler.serialize()
        keystore.key = root_key.serialize(passphrase="SecretRootPP")
        keystore.save()

        subject = DistinguishedNameFactory(
            countryName=root_certificate.dn.countryName,
            stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
            organizationName=root_certificate.dn.organizationName,
            localityName=root_certificate.dn.localityName,
        )

        certificate_request = CertificateFactory(
            type=CertificateTypes.INTERMEDIATE,
            name="test_generate_intermediate_certificate_passphrase",
            parent=root_certificate,
            dn=subject,
        )
        certhandler = Certificate()
        certhandler.create_certificate(
            certificate_request,
            self.key.serialize(passphrase="SecretPP"),
            passphrase="SecretPP",
            passphrase_issuer="SecretRootPP",
        )

        crt = certhandler.certificate
        # subject
        self.assert_subject(crt.subject, certificate_request)
        self.assertEqual(subject.localityName, crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value)

        # issuer
        self.assert_subject(crt.issuer, root_certificate)
        self.assertEqual(subject.localityName, crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value)

    def test_generate_intermediate_certificate_passphrase_wrong_cert_passphrase(self):
        root_key = Key().create_key("ed25519", None)
        root_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
            name="root_test_certificate_passphrase_wrong_cert_passphrase",
        )
        with mute_signals(signals.post_save):
            root_certificate.save()
        root_certhandler = Certificate()
        root_certhandler.create_certificate(
            root_certificate, root_key.serialize(passphrase="SecretRootPP"), passphrase="SecretRootPP"
        )

        keystore = KeyStore(certificate=root_certificate)
        keystore.crt = root_certhandler.serialize()
        keystore.key = root_key.serialize(passphrase="SecretRootPP")
        keystore.save()

        subject = DistinguishedNameFactory(
            countryName=root_certificate.dn.countryName,
            stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
            organizationName=root_certificate.dn.organizationName,
        )

        certificate = CertificateFactory(
            type=CertificateTypes.INTERMEDIATE,
            name="test_certificate_passphrase_wrong_cert_passphrase",
            parent=root_certificate,
            dn=subject,
        )
        certhandler = Certificate()
        with self.assertRaisesMessage(PassPhraseError, "Bad passphrase, could not decode private key"):
            certhandler.create_certificate(
                certificate,
                self.key.serialize(passphrase="SecretPP"),
                passphrase="SecretPPInvalid",
                passphrase_issuer="SecretRootPP",
            )

    def test_generate_intermediate_certificate_passphrase_wrong_issuer_passphrase(self):
        root_key = Key().create_key("ed25519", None)
        root_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
            name="root_test_certificate_passphrase_wrong_issuer_passphrase",
        )
        with mute_signals(signals.post_save):
            root_certificate.save()
        root_certhandler = Certificate()
        root_certhandler.create_certificate(
            root_certificate, root_key.serialize(passphrase="SecretRootPP"), passphrase="SecretRootPP"
        )

        keystore = KeyStore(certificate=root_certificate)
        keystore.crt = root_certhandler.serialize()
        keystore.key = root_key.serialize(passphrase="SecretRootPP")
        keystore.save()

        subject = DistinguishedNameFactory(
            countryName=root_certificate.dn.countryName,
            stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
            organizationName=root_certificate.dn.organizationName,
        )

        certificate = CertificateFactory(
            type=CertificateTypes.INTERMEDIATE,
            name="test_certificate_passphrase_wrong_issuer_passphrase",
            parent=root_certificate,
            dn=subject,
        )
        certhandler = Certificate()
        with self.assertRaisesMessage(PassPhraseError, "Bad passphrase, could not decode issuer key"):
            certhandler.create_certificate(
                certificate,
                self.key.serialize(passphrase="SecretPP"),
                passphrase="SecretPP",
                passphrase_issuer="SecretRootPPInvalid",
            )
