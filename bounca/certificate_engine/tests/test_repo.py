# coding: utf-8
from django.test import TestCase
import os

from bounca.certificate_engine.repo import Repo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_PATH = os.path.join(BASE_DIR, '.testpki/')


class RepoTest(TestCase):

    def test_create_delete_repo_static(self):
        path = TEST_PATH
        self.assertFalse(os.path.isdir(path))
        Repo.create(path)
        self.assertTrue(os.path.isdir(path))
        Repo.delete(path)
        self.assertFalse(os.path.isdir(path))

    def test_create_delete_repo_object(self):
        path = TEST_PATH
        self.assertFalse(os.path.isdir(path))
        Repo(path)
        self.assertTrue(os.path.isdir(path))
        Repo.delete(path)
        self.assertFalse(os.path.isdir(path))
