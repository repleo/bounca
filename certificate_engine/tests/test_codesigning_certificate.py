import arrow
from cryptography.x509 import ExtensionOID

# noinspection PyUnresolvedReferences
from cryptography.x509.oid import ExtendedKeyUsageOID
from django.db.models import signals
from django.utils import timezone
from factory.django import mute_signals

from certificate_engine.ssl.certificate import Certificate, CertificateError
from certificate_engine.ssl.key import Key
from certificate_engine.tests.helpers import CertificateTestCase
from certificate_engine.types import CertificateTypes
from x509_pki.models import KeyStore
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class CodeSigningCertificateTest(CertificateTestCase):
    def setUp(self):
        self.root_key = Key().create_key("ed25519", None)
        subject = DistinguishedNameFactory(
            countryName="NL", stateOrProvinceName="Noord Holland", organizationName="Repleo"
        )

        self.root_certificate = CertificateFactory(
            dn=subject, name="test client root certificate", expires_at=arrow.get(timezone.now()).shift(days=+30).date()
        )

        with mute_signals(signals.post_save):
            self.root_certificate.save()
        root_certhandler = Certificate()
        root_certhandler.create_certificate(self.root_certificate, self.root_key.serialize())
        keystore = KeyStore(certificate=self.root_certificate)
        keystore.crt = root_certhandler.serialize()
        keystore.key = self.root_key.serialize()
        keystore.save()

        self.int_key = Key().create_key("ed25519", None)
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
        )
        self.int_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
            name="test ocsp intermediate certificate",
            type=CertificateTypes.INTERMEDIATE,
            parent=self.root_certificate,
            dn=subject,
            crl_distribution_url="https://example.com/crl/cert.crl",
            ocsp_distribution_host="https://example.com/ocsp/",
        )

        with mute_signals(signals.post_save):
            self.int_certificate.save()

        int_certhandler = Certificate()
        int_certhandler.create_certificate(self.int_certificate, self.int_key.serialize())

        keystore = KeyStore(certificate=self.int_certificate)
        keystore.crt = int_certhandler.serialize()
        keystore.key = self.int_key.serialize()
        keystore.save()

        self.key = Key().create_key("ed25519", None)

    def test_generate_code_signing_certificate(self):
        cs_subject = DistinguishedNameFactory(commonName="cs.example.com")
        certificate = CertificateFactory(
            type=CertificateTypes.CODE_SIGNING_CERT, parent=self.int_certificate, dn=cs_subject
        )
        certhandler = Certificate()
        certhandler.create_certificate(certificate, self.key.serialize())

        crt = certhandler.certificate

        # basicConstraints = CA:FALSE
        # keyUsage = critical, digitalSignature
        self.assert_code_signing_certificate(crt)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.int_key, issuer_certificate=self.int_certificate, critical=False)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt, critical=False)

        # extendedKeyUsage = critical, codeSigning
        self.assert_extension(crt, ExtensionOID.EXTENDED_KEY_USAGE, [ExtendedKeyUsageOID.CODE_SIGNING], critical=True)

        # subject
        self.assert_subject(crt.subject, certificate)
        # issuer
        self.assert_subject(crt.issuer, self.int_certificate)

        # crlDistributionPoints
        self.assert_crl_distribution(crt, self.int_certificate)

    def test_generate_code_signing_certificate_minimal(self):
        cs_subject = DistinguishedNameFactory(
            countryName=None,
            stateOrProvinceName=None,
            localityName=None,
            organizationName=None,
            organizationalUnitName=None,
            emailAddress=None,
            subjectAltNames=["cs.example.com"],
            commonName="cs.example.com",
        )
        certificate = CertificateFactory(
            type=CertificateTypes.CODE_SIGNING_CERT,
            name="test_generate_cs_certificate_minimal",
            parent=self.int_certificate,
            dn=cs_subject,
            crl_distribution_url=None,
            ocsp_distribution_host=None,
        )
        certificate.save()
        certhandler = Certificate()
        certhandler.create_certificate(certificate, self.key.serialize())

        crt = certhandler.certificate

        # basicConstraints = CA:FALSE
        # keyUsage = critical, digitalSignature, keyEncipherment
        self.assert_code_signing_certificate(crt)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.int_key, issuer_certificate=self.int_certificate, critical=False)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt, critical=False)

        # extendedKeyUsage = critical, codeSigning
        self.assert_extension(crt, ExtensionOID.EXTENDED_KEY_USAGE, [ExtendedKeyUsageOID.CODE_SIGNING], critical=True)

        # crlDistributionPoints
        self.assert_crl_distribution(crt, self.int_certificate)

        # subject
        self.assert_subject(crt.subject, certificate)
        # issuer
        self.assert_subject(crt.issuer, self.int_certificate)

    def test_generate_code_signing_certificate_parent_client_cert(self):
        cs_subject = DistinguishedNameFactory(subjectAltNames=["client"])
        certificate = CertificateFactory(
            type=CertificateTypes.CODE_SIGNING_CERT,
            name="test_generate_client_certificate_parent_cs_cert_1",
            parent=self.int_certificate,
            dn=cs_subject,
            crl_distribution_url=None,
            ocsp_distribution_host=None,
        )
        certificate.save()
        certhandler = Certificate()
        certhandler.create_certificate(certificate, self.key.serialize())

        client_subject = DistinguishedNameFactory()
        with self.assertRaises(CertificateError) as context:
            certificate_request = CertificateFactory(
                type=CertificateTypes.CODE_SIGNING_CERT,
                name="test_generate_client_certificate_parent_cs_cert_2",
                parent=certificate,
                dn=client_subject,
            )
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request, self.key.serialize())

        self.assertEqual("A root or intermediate parent is expected", str(context.exception))
