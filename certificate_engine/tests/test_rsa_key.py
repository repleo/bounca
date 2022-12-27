import arrow
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization.pkcs12 import load_pkcs12
from django.db.models import signals
from django.test import TestCase
from django.utils import timezone
from factory.django import mute_signals

from certificate_engine.ssl.certificate import Certificate
from certificate_engine.ssl.key import Key
from certificate_engine.types import CertificateTypes
from x509_pki.models import KeyStore
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class KeyRsaTest(TestCase):
    def test_generate_private_key_2048(self):
        keyhandler = Key()
        keyhandler.create_key("rsa", 2048)
        self.assertEqual(keyhandler.key.key_size, 2048)
        pkey = keyhandler.key.public_key()
        self.assertIsInstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_generate_private_key_4096(self):
        prvkey = Key().create_key("rsa", 4096)
        self.assertEqual(prvkey.key.key_size, 4096)
        pkey = prvkey.key.public_key()
        self.assertIsInstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_serialize_keys_passphrase(self):
        key = Key()
        key.create_key("rsa", 4096)
        pem = key.serialize("test_store_keys_passphrase")
        prvkey = key.load(pem, "test_store_keys_passphrase")
        self.assertIsInstance(prvkey.key, rsa.RSAPrivateKey)
        self.assertEqual(prvkey.key.key_size, 4096)

    def test_store_keys_no_object(self):
        key = Key()
        with self.assertRaisesMessage(RuntimeError, "No key object"):
            key.serialize("test_store_keys_passphrase")

    def test_store_keys_no_passphrase(self):
        key = Key()
        key.create_key("rsa", 2048)
        pem = key.serialize()
        key = Key()
        prvkey = key.load(pem)
        self.assertIsInstance(prvkey.key, rsa.RSAPrivateKey)
        self.assertEqual(prvkey.key.key_size, 2048)

    def test_store_keys_wrong_passphrase(self):
        key = Key()
        key.create_key("rsa", 2048)
        pem = key.serialize("test_store_keys_wrong_passphrase")
        with self.assertRaisesMessage(ValueError, "Bad decrypt. Incorrect password?"):
            key.load(pem, "test_store_keys_passphrase")

    def test_check_passphrase_valid(self):
        key = Key()
        key.create_key("rsa", 2048)
        pem = key.serialize("check_passphrase")
        self.assertTrue(key.check_passphrase(pem, "check_passphrase"))

    def test_check_passphrase_invalid(self):
        key = Key()
        key.create_key("rsa", 2048)
        pem = key.serialize("test_check_passphrase_invalid")
        self.assertFalse(key.check_passphrase(pem, "check_passphrase"))

    def test_serialize_pkcs12_no_key(self):
        key = Key()

        with self.assertRaisesMessage(RuntimeError, "No key object"):
            key.serialize_pkcs12("test_pkcs12", None)

    def test_serialize_pkcs12_no_name(self):
        key = Key()
        key.create_key("rsa", 4096)

        with self.assertRaisesMessage(ValueError, "No name provided"):
            key.serialize_pkcs12("", None)

    def test_serialize_pkcs12_no_certificate(self):
        key = Key()
        key.create_key("rsa", 4096)

        with self.assertRaisesMessage(ValueError, "No certificate provided"):
            key.serialize_pkcs12("test_pkcs12", None)

    def test_serialize_pkcs12_nopassphrase(self):
        subject = DistinguishedNameFactory(
            localityName="Amsterdam",
            organizationalUnitName="BounCA Root",
        )

        key = Key()
        key.create_key("rsa", 4096)

        certificate_request = CertificateFactory(dn=subject)
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, key.serialize())

        crt = certhandler.certificate

        pkcs12 = key.serialize_pkcs12("test_pkcs12", crt)
        pkcs12_obj = load_pkcs12(pkcs12, None)

        self.assertEqual(pkcs12_obj.key.key_size, 4096)
        self.assertEqual(pkcs12_obj.cert.friendly_name.decode("utf-8"), "test_pkcs12")
        self.assertEqual(pkcs12_obj.cert.certificate.serial_number, crt.serial_number)

    def test_serialize_pkcs12_passphrase(self):
        subject = DistinguishedNameFactory(
            localityName="Amsterdam",
            organizationalUnitName="BounCA Root",
        )

        key = Key()
        key.create_key("rsa", 4096)

        certificate_request = CertificateFactory(dn=subject)
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, key.serialize())

        crt = certhandler.certificate

        pkcs12 = key.serialize_pkcs12("test_pkcs12", crt, "testpassphrase")
        pkcs12_obj = load_pkcs12(pkcs12, "testpassphrase".encode("utf-8"))

        self.assertEqual(pkcs12_obj.key.key_size, 4096)
        self.assertEqual(pkcs12_obj.cert.friendly_name.decode("utf-8"), "test_pkcs12")
        self.assertEqual(pkcs12_obj.cert.certificate.serial_number, crt.serial_number)

    def test_serialize_pkcs12_cas_nopassphrase(self):
        root_key = Key().create_key("ed25519", None)
        subject = DistinguishedNameFactory(
            countryName="NL", stateOrProvinceName="Noord Holland", organizationName="Repleo"
        )

        root_certificate = CertificateFactory(
            dn=subject, name="test_server_root_certificate", expires_at=arrow.get(timezone.now()).shift(days=+30).date()
        )

        with mute_signals(signals.post_save):
            root_certificate.save()
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate, root_key.serialize())
        keystore = KeyStore(certificate=root_certificate)
        keystore.crt = root_certhandler.serialize()
        keystore.key = root_key.serialize()
        keystore.save()

        int_key = Key().create_key("rsa", 2048)
        subject = DistinguishedNameFactory(
            countryName=root_certificate.dn.countryName,
            stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
            organizationName=root_certificate.dn.organizationName,
        )
        int_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
            name="test_server_intermediate_certificate",
            type=CertificateTypes.INTERMEDIATE,
            parent=root_certificate,
            dn=subject,
            crl_distribution_url="https://example.com/crl/cert.crl",
            ocsp_distribution_host="https://example.com/ocsp/",
        )

        with mute_signals(signals.post_save):
            int_certificate.save()

        int_certhandler = Certificate()
        int_certhandler.create_certificate(int_certificate, int_key.serialize())

        keystore = KeyStore(certificate=int_certificate)
        keystore.crt = int_certhandler.serialize()
        keystore.key = int_key.serialize()
        keystore.save()

        pkcs12 = int_key.serialize_pkcs12(
            "test_pkcs12_cas", int_certhandler.certificate, cas=[root_certhandler.certificate]
        )
        pkcs12_obj = load_pkcs12(pkcs12, None)

        self.assertEqual(pkcs12_obj.key.key_size, 2048)
        self.assertEqual(pkcs12_obj.cert.friendly_name.decode("utf-8"), "test_pkcs12_cas")
        self.assertEqual(pkcs12_obj.cert.certificate.serial_number, int_certhandler.certificate.serial_number)
        self.assertEqual(
            pkcs12_obj.additional_certs[0].certificate.serial_number, root_certhandler.certificate.serial_number
        )
