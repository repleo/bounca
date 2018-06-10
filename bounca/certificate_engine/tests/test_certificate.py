# coding: utf-8

from bounca.certificate_engine.ssl.certificate import Certificate
from bounca.certificate_engine.tests.testcases import CertificateTestCase


class CertificateTest(CertificateTestCase):

    def test_generate_root_ca(self):
        certhandler = Certificate(self.repo)
        certhandler.create_certificate({})
        # print(certhandler.certificate)
