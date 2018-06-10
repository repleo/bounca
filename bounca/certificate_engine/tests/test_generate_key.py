# coding: utf-8
from cryptography.hazmat.primitives.asymmetric import rsa

from bounca.certificate_engine.ssl.generate_key import createKey
from bounca.certificate_engine.tests.testcases import CertificateTestCase


class GenerateKeyTest(CertificateTestCase):

    def test_generate_private_key_2048(self):
        key = createKey(2048)
        self.assertEqual(key.key_size, 2048)
        pkey = key.public_key()
        self.assertIsInstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_generate_private_key_4096(self):
        key = createKey(4096)
        self.assertEqual(key.key_size, 4096)
        pkey = key.public_key()
        self.assertIsInstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_store_keys_passphrase(self):
        key = createKey(4096)
        self.repo.write_private_key(key, 'test.key.pem', b'test_store_keys_passphrase')
        key = self.repo.read_private_key('test.key.pem', b'test_store_keys_passphrase')
        self.assertIsInstance(key, rsa.RSAPrivateKey)
        self.assertEqual(key.key_size, 4096)

    def test_store_keys_no_passphrase(self):
        key = createKey(4096)
        self.repo.write_private_key(key, 'test.key.pem')
        key = self.repo.read_private_key('test.key.pem')
        self.assertIsInstance(key, rsa.RSAPrivateKey)
        self.assertEqual(key.key_size, 4096)

    def test_store_keys_wrong_passphrase(self):
        key = createKey(4096)
        self.repo.write_private_key(key, 'test.key.pem', b'test_store_keys_wrong_passphrase')
        with self.assertRaisesMessage(ValueError, 'Bad decrypt. Incorrect password?'):
            self.repo.read_private_key('test.key.pem', b'test_store_keys_passphrase')

    def test_store_keys_file_not_found(self):
        key = createKey(4096)
        self.repo.write_private_key(key, 'test.key.pem', b'test_store_keys_wrong_passphrase')
        with self.assertRaisesRegex(FileNotFoundError, r'.*bounca/certificate_engine/.testpki/notfound.key.pem\'$'):
            self.repo.read_private_key('notfound.key.pem', b'test_store_keys_passphrase')

    def test_check_passphrase_valid(self):
        key = createKey(4096)
        self.repo.write_private_key(key, 'test.key.pem', b'check_passphrase')
        self.assertTrue(self.repo.check_passphrase('test.key.pem', b'check_passphrase'))

    def test_check_passphrase_invalid(self):
        key = createKey(4096)
        self.repo.write_private_key(key, 'test.key.pem', b'test_check_passphrase_invalid')
        self.assertFalse(self.repo.check_passphrase('test.key.pem', b'check_passphrase'))

    def test_check_passphrase_file_not_found(self):
        key = createKey(4096)
        self.repo.write_private_key(key, 'test.key.pem', b'test_check_passphrase_file_not_found')
        with self.assertRaisesRegex(FileNotFoundError, r'.*bounca/certificate_engine/.testpki/notfound.key.pem\'$'):
            self.repo.check_passphrase('notfound.key.pem', b'test_store_keys_passphrase')

        # """
        # Verify that calling ``Context.use_privatekey_file`` with the given
        # arguments does not raise an exception.
        # """
        # key = PKey()
        # key.generate_key(TYPE_RSA, 512)
        #
        # with open(pemfile, "wt") as pem:
        #     pem.write(
        #         dump_privatekey(FILETYPE_PEM, key).decode("ascii")
        #     )
        #
        # ctx = Context(TLSv1_METHOD)
        # ctx.use_privatekey_file(pemfile, filetype)
