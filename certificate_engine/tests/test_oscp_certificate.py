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


class OcspCertificateTest(CertificateTestCase):
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

    def test_generate_ocsp_certificate(self):
        ocsp_subject = DistinguishedNameFactory(commonName="ocsp.example.com")
        certificate = CertificateFactory(type=CertificateTypes.OCSP, parent=self.int_certificate, dn=ocsp_subject)
        certhandler = Certificate()
        certhandler.create_certificate(certificate, self.key.serialize())

        crt = certhandler.certificate

        # basicConstraints = CA:FALSE
        # keyUsage = critical, digitalSignature
        self.assert_ocsp_certificate(crt)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.int_key, issuer_certificate=self.int_certificate, critical=False)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt, critical=False)

        # extendedKeyUsage = critical, OCSPSigning
        self.assert_extension(crt, ExtensionOID.EXTENDED_KEY_USAGE, [ExtendedKeyUsageOID.OCSP_SIGNING], critical=True)

        # subject
        self.assert_subject(crt.subject, certificate)
        # issuer
        self.assert_subject(crt.issuer, self.int_certificate)

        # crlDistributionPoints
        self.assert_crl_distribution(crt, self.int_certificate)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        self.assert_oscp(crt, self.int_certificate)

    def test_generate_ocsp_certificate_minimal(self):
        ocsp_subject = DistinguishedNameFactory(
            countryName=None,
            stateOrProvinceName=None,
            localityName=None,
            organizationName=None,
            organizationalUnitName=None,
            emailAddress=None,
            subjectAltNames=["ocsp.example.com"],
            commonName="ocsp.example.com",
        )
        certificate = CertificateFactory(
            type=CertificateTypes.OCSP,
            name="test_generate_ocsp_certificate_minimal",
            parent=self.int_certificate,
            dn=ocsp_subject,
            crl_distribution_url=None,
            ocsp_distribution_host=None,
        )
        certificate.save()
        certhandler = Certificate()
        certhandler.create_certificate(certificate, self.key.serialize())

        crt = certhandler.certificate

        # basicConstraints = CA:FALSE
        # keyUsage = critical, digitalSignature, keyEncipherment
        self.assert_ocsp_certificate(crt)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.int_key, issuer_certificate=self.int_certificate, critical=False)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt, critical=False)

        # extendedKeyUsage = critical, OCSPSigning
        self.assert_extension(crt, ExtensionOID.EXTENDED_KEY_USAGE, [ExtendedKeyUsageOID.OCSP_SIGNING], critical=True)

        # crlDistributionPoints
        self.assert_crl_distribution(crt, self.int_certificate)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        self.assert_oscp(crt, self.int_certificate)

        # subject
        self.assert_subject(crt.subject, certificate)
        # issuer
        self.assert_subject(crt.issuer, self.int_certificate)

    def test_generate_ocsp_certificate_parent_client_cert(self):
        ocsp_subject = DistinguishedNameFactory(subjectAltNames=["client"])
        certificate = CertificateFactory(
            type=CertificateTypes.OCSP,
            name="test_generate_client_certificate_parent_ocsp_cert_1",
            parent=self.int_certificate,
            dn=ocsp_subject,
            crl_distribution_url=None,
            ocsp_distribution_host=None,
        )
        certificate.save()
        certhandler = Certificate()
        certhandler.create_certificate(certificate, self.key.serialize())

        client_subject = DistinguishedNameFactory()
        with self.assertRaises(CertificateError) as context:
            certificate_request = CertificateFactory(
                type=CertificateTypes.OCSP,
                name="test_generate_client_certificate_parent_ocsp_cert_2",
                parent=certificate,
                dn=client_subject,
            )
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request, self.key.serialize())

        self.assertEqual("A root or intermediate parent is expected", str(context.exception))
