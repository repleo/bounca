# import os

# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization

from bounca.certificate_engine.repo import Repo


class Certificate(object):

    def __init__(self, repo):
        if not isinstance(repo, Repo):
            raise RuntimeError("Provide a valid repo")
        self._repo = repo
        self._certificate = None

    @property
    def certificate(self):
        return self._certificate

    def create_certificate(self, profile):
        """
        Create a certificate.

        Arguments:
        Returns:   The certificate
        """

        return self._certificate
