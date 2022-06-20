# coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.test import TestCase

from api.tests.factories import AuthorisedAppFactory


class FactoriesTest(TestCase):
    """
    Very simple tests to ensure the factories work as expected.
    """

    def test_authorised_app_factory(self):
        authorised_app = AuthorisedAppFactory()
        self.assertTrue(authorised_app.id is not None)
        self.assertTrue(len(authorised_app.name) > 1)
        self.assertTrue(authorised_app.user is not None)
        # Base64 encoding of 16 bit random number
        self.assertTrue(len(authorised_app.token) == 44)
