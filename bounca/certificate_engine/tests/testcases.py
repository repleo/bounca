import os

from django.test import TestCase

from bounca.certificate_engine.repo import Repo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_PATH = os.path.join(BASE_DIR, '.testpki/')


class CertificateTestCase(TestCase):
    """ This TestCase allows setups a dummy SSL workdir. """

    @classmethod
    def setUpClass(cls):
        cls.repo = Repo(TEST_PATH)
        super(CertificateTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        Repo.delete(TEST_PATH)
        super(CertificateTestCase, cls).tearDownClass()
