# coding: utf-8

from bounca.certificate_engine.ssl.certificate import Certificate
from bounca.certificate_engine.ssl.key import Key
from bounca.certificate_engine.tests.testcases import CertificateTestCase


class CertificateTest(CertificateTestCase):

    def test_generate_root_ca(self):
        key = Key(self.repo)
        key.create_key(2048)
        certhandler = Certificate(self.repo)
        certhandler.create_certificate(key)
        # print(certhandler.certificate)
