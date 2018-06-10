# coding: utf-8
import os
from stat import ST_MODE

from cryptography.hazmat.primitives.asymmetric import rsa

from bounca.certificate_engine.ssl.key import Key
from bounca.certificate_engine.tests.testcases import CertificateTestCase


class KeyTest(CertificateTestCase):

    def test_generate_private_key_2048(self):
        keyhandler = Key(self.repo)
        keyhandler.create_key(2048)
        self.assertEqual(keyhandler.key.key_size, 2048)
        pkey = keyhandler.key.public_key()
        self.assertIsInstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_generate_private_key_4096(self):
        prvkey = Key(self.repo).create_key(4096)
        self.assertEqual(prvkey.key_size, 4096)
        pkey = prvkey.public_key()
        self.assertIsInstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_store_keys_passphrase(self):
        key = Key(self.repo)
        key.create_key(4096)
        key.write_private_key('test.key.pem', b'test_store_keys_passphrase')
        # check if generate file is only readable by myself
        self.assertEqual(oct(os.stat(os.path.join(self.repo.base, 'test.key.pem'))[ST_MODE]), '0o100400')
        prvkey = key.read_private_key('test.key.pem', b'test_store_keys_passphrase')
        self.assertIsInstance(prvkey, rsa.RSAPrivateKey)
        self.assertEqual(prvkey.key_size, 4096)

    def test_store_keys_no_passphrase(self):
        key = Key(self.repo)
        key.create_key(2048)
        key.write_private_key('test.key.pem')
        key = Key(self.repo)
        prvkey = key.read_private_key('test.key.pem')
        self.assertIsInstance(prvkey, rsa.RSAPrivateKey)
        self.assertEqual(prvkey.key_size, 2048)

    def test_store_keys_wrong_passphrase(self):
        key = Key(self.repo)
        key.create_key(2048)
        key.write_private_key('test.key.pem', b'test_store_keys_wrong_passphrase')
        with self.assertRaisesMessage(ValueError, 'Bad decrypt. Incorrect password?'):
            key.read_private_key('test.key.pem', b'test_store_keys_passphrase')

    def test_store_keys_file_not_found(self):
        key = Key(self.repo)
        key.create_key(2048)
        key.write_private_key('test.key.pem', b'test_store_keys_wrong_passphrase')
        with self.assertRaisesRegex(FileNotFoundError, r'.*bounca/certificate_engine/.testpki/notfound.key.pem\'$'):
            key.read_private_key('notfound.key.pem', b'test_store_keys_passphrase')

    def test_check_passphrase_valid(self):
        key = Key(self.repo)
        key.create_key(2048)
        key.write_private_key('test.key.pem', b'check_passphrase')
        self.assertTrue(key.check_passphrase('test.key.pem', b'check_passphrase'))

    def test_check_passphrase_invalid(self):
        key = Key(self.repo)
        key.create_key(2048)
        key.write_private_key('test.key.pem', b'test_check_passphrase_invalid')
        self.assertFalse(key.check_passphrase('test.key.pem', b'check_passphrase'))

    def test_check_passphrase_file_not_found(self):
        key = Key(self.repo)
        key.create_key(2048)
        key.write_private_key('test.key.pem', b'test_check_passphrase_file_not_found')
        with self.assertRaisesRegex(FileNotFoundError, r'.*bounca/certificate_engine/.testpki/notfound.key.pem\'$'):
            key.check_passphrase('notfound.key.pem', b'test_store_keys_passphrase')
