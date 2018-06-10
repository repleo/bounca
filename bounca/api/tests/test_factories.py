# coding: utf-8
from django.test import TestCase

from .factories import UserFactory


class FactoriesTest(TestCase):
    """
    Very simple tests to ensure the factories work as expected.
    """

    def test_user_factory(self):
        user = UserFactory()
        self.assertIsNotNone(user.username)
        self.assertIsNotNone(user.password)
        self.assertIsNotNone(user.first_name)
        self.assertIsNotNone(user.last_name)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
