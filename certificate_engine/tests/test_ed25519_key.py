from cryptography.hazmat.primitives.asymmetric import ed25519
from django.test import TestCase

from certificate_engine.ssl.key import Key


class KeyEd25519Test(TestCase):
    def test_generate_private_key(self):
        keyhandler = Key()
        keyhandler.create_key("ed25519", None)
        data = b"testdata"
        signature = keyhandler.key.sign(data)
        pkey = keyhandler.key.public_key()
        self.assertIsNotNone(pkey)
        # would throw InvalidSignature if not correct
        pkey.verify(signature, data)
        self.assertIsNotNone(keyhandler.key)

    def test_serialize_keys_passphrase(self):
        key = Key()
        key.create_key("ed25519", None)
        pem = key.serialize("test_store_keys_passphrase")
        prvkey = key.load(pem, "test_store_keys_passphrase")
        self.assertIsInstance(prvkey.key, ed25519.Ed25519PrivateKey)

    def test_store_keys_no_object(self):
        key = Key()
        with self.assertRaisesMessage(RuntimeError, "No key object"):
            key.serialize("test_store_keys_passphrase")

    def test_store_keys_no_passphrase(self):
        key = Key()
        key.create_key("ed25519", None)
        pem = key.serialize()
        key = Key()
        prvkey = key.load(pem)
        self.assertIsInstance(prvkey.key, ed25519.Ed25519PrivateKey)

    def test_store_keys_wrong_passphrase(self):
        key = Key()
        key.create_key("ed25519", None)
        pem = key.serialize("test_store_keys_wrong_passphrase")
        with self.assertRaisesMessage(ValueError, "Bad decrypt. Incorrect password?"):
            key.load(pem, "test_store_keys_passphrase")

    def test_check_passphrase_valid(self):
        key = Key()
        key.create_key("ed25519", None)
        pem = key.serialize("check_passphrase")
        self.assertTrue(key.check_passphrase(pem, "check_passphrase"))

    def test_check_passphrase_invalid(self):
        key = Key()
        key.create_key("ed25519", None)
        pem = key.serialize("test_check_passphrase_invalid")
        self.assertFalse(key.check_passphrase(pem, "check_passphrase"))
