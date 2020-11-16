from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import TestCase

from certificate_engine.ssl.key import Key


class KeyTest(TestCase):

    def test_generate_private_key_2048(self):
        keyhandler = Key()
        keyhandler.create_key(2048)
        self.assertEqual(keyhandler.key.key_size, 2048)
        pkey = keyhandler.key.public_key()
        self.assertIsInstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_generate_private_key_4096(self):
        prvkey = Key().create_key(4096)
        self.assertEqual(prvkey.key.key_size, 4096)
        pkey = prvkey.key.public_key()
        self.assertIsInstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_serialize_keys_passphrase(self):
        key = Key()
        key.create_key(4096)
        pem = key.serialize('test_store_keys_passphrase')
        prvkey = key.load(pem, 'test_store_keys_passphrase')
        self.assertIsInstance(prvkey.key, rsa.RSAPrivateKey)
        self.assertEqual(prvkey.key.key_size, 4096)

    def test_store_keys_no_object(self):
        key = Key()
        with self.assertRaisesMessage(RuntimeError, "No key object"):
            key.serialize('test_store_keys_passphrase')

    def test_store_keys_no_passphrase(self):
        key = Key()
        key.create_key(2048)
        pem = key.serialize()
        key = Key()
        prvkey = key.load(pem)
        self.assertIsInstance(prvkey.key, rsa.RSAPrivateKey)
        self.assertEqual(prvkey.key.key_size, 2048)

    def test_store_keys_wrong_passphrase(self):
        key = Key()
        key.create_key(2048)
        pem = key.serialize('test_store_keys_wrong_passphrase')
        with self.assertRaisesMessage(ValueError, 'Bad decrypt. Incorrect password?'):
            key.load(pem, 'test_store_keys_passphrase')

    def test_check_passphrase_valid(self):
        key = Key()
        key.create_key(2048)
        pem = key.serialize('check_passphrase')
        self.assertTrue(key.check_passphrase(pem, 'check_passphrase'))

    def test_check_passphrase_invalid(self):
        key = Key()
        key.create_key(2048)
        pem = key.serialize('test_check_passphrase_invalid')
        self.assertFalse(key.check_passphrase(pem, 'check_passphrase'))
