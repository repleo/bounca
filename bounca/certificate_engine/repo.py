
import os
import shutil

from django.conf import settings


REPO_PATH = settings.CERTIFICATE_REPO_PATH


class Repo(object):
    """ Repo handler for certificate files """

    @staticmethod
    def create(path=REPO_PATH):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def delete(path=REPO_PATH):
        shutil.rmtree(path)

    def __init__(self, path=REPO_PATH):
        self._base = path
        self.create(self._base)

    @property
    def base(self):
        return self._base

    def make_repo_path(self, path):
        return os.path.join(self._base, path)
