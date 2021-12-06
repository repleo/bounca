# coding: utf-8
from datetime import datetime, timedelta

import arrow
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.db.models import signals
from django.utils import timezone
from factory.django import mute_signals

from certificate_engine.ssl.certificate import Certificate
from certificate_engine.ssl.crl import revocation_builder, revocation_list_builder, serialize
from certificate_engine.ssl.key import Key
from certificate_engine.tests.helpers import CertificateTestCase
from certificate_engine.types import CertificateTypes
from x509_pki.models import KeyStore
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class CRLClientServerTest(CertificateTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_key = Key().create_key("rsa", 4096)
        subject = DistinguishedNameFactory(
            countryName="NL",
            stateOrProvinceName="Noord Holland",
            organizationName="Repleo",
            commonName="BounCA test CA",
        )

        cls.root_certificate = CertificateFactory(
            dn=subject, name="test_server_root_certificate", expires_at=arrow.get(timezone.now()).shift(days=+30).date()
        )

        with mute_signals(signals.post_save):
            cls.root_certificate.save()
        root_certhandler = Certificate()
        root_certhandler.create_certificate(cls.root_certificate, cls.root_key.serialize())
        keystore = KeyStore(certificate=cls.root_certificate)
        keystore.crt = root_certhandler.serialize()
        keystore.key = cls.root_key.serialize()
        keystore.save()

        cls.int_key = Key().create_key("rsa", 4096)
        subject = DistinguishedNameFactory(
            countryName=cls.root_certificate.dn.countryName,
            stateOrProvinceName=cls.root_certificate.dn.stateOrProvinceName,
            organizationName=cls.root_certificate.dn.organizationName,
            commonName="BounCA test Int CA",
        )
        cls.int_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
            name="test_server_intermediate_certificate",
            type=CertificateTypes.INTERMEDIATE,
            parent=cls.root_certificate,
            dn=subject,
        )

        with mute_signals(signals.post_save):
            cls.int_certificate.save()

        int_certhandler = Certificate()
        int_certhandler.create_certificate(cls.int_certificate, cls.int_key.serialize())

        keystore = KeyStore(certificate=cls.int_certificate)
        keystore.crt = int_certhandler.serialize()
        keystore.key = cls.int_key.serialize()
        keystore.save()

        cls.key = Key().create_key("rsa", 4096)

    def make_server_certificate(self):
        server_subject = DistinguishedNameFactory(
            subjectAltNames=["www.repleo.nl", "*.bounca.org", "www.mac-usb-serial.com", "127.0.0.1"]
        )
        certificate = CertificateFactory(
            type=CertificateTypes.SERVER_CERT,
            name="test_generate_server_certificate",
            parent=self.int_certificate,
            dn=server_subject,
            crl_distribution_url=None,
            ocsp_distribution_host=None,
        )
        certhandler = Certificate()
        certhandler.create_certificate(certificate, self.key.serialize())

        crt = certhandler.certificate
        return crt, crt.public_bytes(encoding=serialization.Encoding.PEM).decode("utf8")

    def test_revocation_builder(self):
        timestamp = datetime.today()
        cert, pem = self.make_server_certificate()
        revoked_cert = revocation_builder(pem, timestamp)
        self.assertEqual(revoked_cert.serial_number, cert.serial_number)
        self.assertEqual(revoked_cert.revocation_date, timestamp)
        self.assertEqual(len(revoked_cert.extensions), 0)

    def test_revocation_list_builder_empty(self):
        last_update = datetime.today().replace(microsecond=0) - timedelta(3, 0, 0)
        next_update = datetime.today().replace(microsecond=0) + timedelta(2, 0, 0)
        crl = revocation_list_builder(
            [],
            self.int_certificate.keystore.crt,
            self.int_certificate.keystore.key,
            last_update=last_update,
            next_update=next_update,
        )
        cert, pem = self.make_server_certificate()
        self.assertEqual(crl.issuer.rdns[0]._attributes[0].value, "BounCA test Int CA")
        self.assertEqual(crl.last_update, last_update)
        self.assertEqual(crl.next_update, next_update)
        self.assertIsNone(crl.get_revoked_certificate_by_serial_number(cert.serial_number))

    def test_revocation_list_builder_one_cert(self):
        cert, pem = self.make_server_certificate()
        revoke_date = datetime.today().replace(microsecond=0) - timedelta(3, 0, 0)
        crl = revocation_list_builder(
            [(pem, revoke_date)], self.int_certificate.keystore.crt, self.int_certificate.keystore.key
        )
        self.assertEqual(crl.issuer.rdns[0]._attributes[0].value, "BounCA test Int CA")
        self.assertEqual(crl.get_revoked_certificate_by_serial_number(cert.serial_number).revocation_date, revoke_date)

    def test_revocation_list_builder_one_cert_passphrase(self):
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
            commonName="BounCA test Int passphrase CA",
        )
        int_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
            name="test_server_intermediate_certificate_pass",
            type=CertificateTypes.INTERMEDIATE,
            parent=self.root_certificate,
            dn=subject,
        )

        with mute_signals(signals.post_save):
            int_certificate.save()
        int_key = Key().create_key("rsa", 4096)
        int_certhandler = Certificate()
        int_certhandler.create_certificate(int_certificate, int_key.serialize())

        keystore = KeyStore(certificate=int_certificate)
        keystore.crt = int_certhandler.serialize()
        keystore.key = int_key.serialize(passphrase="testphrase")
        keystore.save()

        crl = revocation_list_builder([], int_certificate.keystore.crt, int_certificate.keystore.key, "testphrase")
        self.assertEqual(crl.issuer.rdns[0]._attributes[0].value, "BounCA test Int passphrase CA")

    def test_revocation_list_builder_serialization(self):
        crl = revocation_list_builder([], self.int_certificate.keystore.crt, self.int_certificate.keystore.key)
        pem = serialize(crl)
        self.assertIn("-----BEGIN X509 CRL-----", pem)
        crl_deserialized = x509.load_pem_x509_crl(pem.encode("utf8"), backend=default_backend())
        self.assertEqual(crl_deserialized.issuer.rdns[0]._attributes[0].value, "BounCA test Int CA")


class CRLIntermediateTest(CertificateTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_key = Key().create_key("rsa", 4096)
        subject = DistinguishedNameFactory(
            countryName="NL",
            stateOrProvinceName="Noord Holland",
            organizationName="Repleo",
            commonName="BounCA test CA",
        )

        cls.root_certificate = CertificateFactory(
            dn=subject, name="test_server_root_certificate", expires_at=arrow.get(timezone.now()).shift(days=+30).date()
        )

        with mute_signals(signals.post_save):
            cls.root_certificate.save()
        root_certhandler = Certificate()
        root_certhandler.create_certificate(cls.root_certificate, cls.root_key.serialize())
        keystore = KeyStore(certificate=cls.root_certificate)
        keystore.crt = root_certhandler.serialize()
        keystore.key = cls.root_key.serialize()
        keystore.save()

    def make_intermediate_certificate(self):
        int_key = Key().create_key("rsa", 4096)
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
            commonName="BounCA test Int CA",
        )
        int_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
            name="test_server_intermediate_certificate",
            type=CertificateTypes.INTERMEDIATE,
            parent=self.root_certificate,
            dn=subject,
        )

        int_certificate.save()

        int_certhandler = Certificate()
        int_certhandler.create_certificate(int_certificate, int_key.serialize())

        crt = int_certhandler.certificate
        return crt, crt.public_bytes(encoding=serialization.Encoding.PEM).decode("utf8")

    def test_revocation_builder(self):
        timestamp = datetime.today()
        cert, pem = self.make_intermediate_certificate()
        revoked_cert = revocation_builder(pem, timestamp)
        self.assertEqual(revoked_cert.serial_number, cert.serial_number)
        self.assertEqual(revoked_cert.revocation_date, timestamp)
        self.assertEqual(len(revoked_cert.extensions), 0)

    def test_revocation_list_builder_empty(self):
        last_update = datetime.today().replace(microsecond=0) - timedelta(3, 0, 0)
        next_update = datetime.today().replace(microsecond=0) + timedelta(2, 0, 0)
        crl = revocation_list_builder(
            [],
            self.root_certificate.keystore.crt,
            self.root_certificate.keystore.key,
            last_update=last_update,
            next_update=next_update,
        )
        cert, pem = self.make_intermediate_certificate()
        self.assertEqual(crl.issuer.rdns[0]._attributes[0].value, "BounCA test CA")
        self.assertEqual(crl.last_update, last_update)
        self.assertEqual(crl.next_update, next_update)
        self.assertIsNone(crl.get_revoked_certificate_by_serial_number(cert.serial_number))

    def test_revocation_list_builder_one_cert(self):
        cert, pem = self.make_intermediate_certificate()
        revoke_date = datetime.today().replace(microsecond=0) - timedelta(3, 0, 0)
        crl = revocation_list_builder(
            [(pem, revoke_date)], self.root_certificate.keystore.crt, self.root_certificate.keystore.key
        )
        self.assertEqual(crl.issuer.rdns[0]._attributes[0].value, "BounCA test CA")
        self.assertEqual(crl.get_revoked_certificate_by_serial_number(cert.serial_number).revocation_date, revoke_date)

    def test_revocation_list_builder_one_cert_passphrase(self):
        subject = DistinguishedNameFactory(
            countryName=self.root_certificate.dn.countryName,
            stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
            organizationName=self.root_certificate.dn.organizationName,
            commonName="BounCA test Int passphrase CA",
        )
        int_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
            name="test_server_intermediate_certificate_pass",
            type=CertificateTypes.INTERMEDIATE,
            parent=self.root_certificate,
            dn=subject,
        )

        with mute_signals(signals.post_save):
            int_certificate.save()
        int_key = Key().create_key("rsa", 4096)
        int_certhandler = Certificate()
        int_certhandler.create_certificate(int_certificate, int_key.serialize())

        keystore = KeyStore(certificate=int_certificate)
        keystore.crt = int_certhandler.serialize()
        keystore.key = int_key.serialize(passphrase="testphrase")
        keystore.save()

        crl = revocation_list_builder([], int_certificate.keystore.crt, int_certificate.keystore.key, "testphrase")
        self.assertEqual(crl.issuer.rdns[0]._attributes[0].value, "BounCA test Int passphrase CA")

    def test_revocation_list_builder_serialization(self):
        crl = revocation_list_builder([], self.root_certificate.keystore.crt, self.root_certificate.keystore.key)
        pem = serialize(crl)
        self.assertIn("-----BEGIN X509 CRL-----", pem)
        crl_deserialized = x509.load_pem_x509_crl(pem.encode("utf8"), backend=default_backend())
        self.assertEqual(crl_deserialized.issuer.rdns[0]._attributes[0].value, "BounCA test CA")
