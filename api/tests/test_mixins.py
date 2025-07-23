from __future__ import absolute_import, unicode_literals

from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.serializers import Serializer, ValidationError

from api.mixins import TrapDjangoValidationErrorCreateMixin
from certificate_engine.ssl.certificate import PolicyError


class MockSerializer(Serializer):
    def save(self):
        pass


class TrapDjangoValidationErrorCreateMixinTest(TestCase):
    def setUp(self):
        self.mixin = TrapDjangoValidationErrorCreateMixin()
        self.serializer = Mock(spec=MockSerializer)

    def test_perform_create_success(self):
        self.serializer.save = Mock(return_value=True)
        try:
            self.mixin.perform_create(self.serializer)
        except Exception as e:
            self.fail(f"perform_create() raised an exception when it should not: {e}")

    def test_perform_create_django_validation_error(self):
        self.serializer.save = Mock(side_effect=DjangoValidationError(["Test error message"]))
        with self.assertRaises(ValidationError) as context:
            self.mixin.perform_create(self.serializer)
        self.assertIn("non_field_errors", context.exception.detail)
        self.assertEqual(context.exception.detail["non_field_errors"], ["Test error message"])

    def test_perform_create_policy_error(self):
        self.serializer.save = Mock(side_effect=PolicyError("Policy error occurred"))
        with self.assertRaises(ValidationError) as context:
            self.mixin.perform_create(self.serializer)
        self.assertEqual(str(context.exception.detail), "Policy error occurred")
