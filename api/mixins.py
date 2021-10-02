"""Create serializer validation errors from django validation errors for automatic handling"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from certificate_engine.ssl.certificate import PolicyError


class TrapDjangoValidationErrorCreateMixin(object):

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as detail:
            raise serializers.ValidationError({'non_field_errors': detail.messages})
        except PolicyError as detail:
            raise serializers.ValidationError(detail.args[0])


class TrapDjangoValidationErrorUpdateMixin(object):

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as detail:
            raise serializers.ValidationError({'non_field_errors': detail.messages})
        except PolicyError as detail:
            raise serializers.ValidationError(detail.args[0])
