"""Create serializer validation errors from django validation errors for automatic handling"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class TrapDjangoValidationErrorCreateMixin(object):

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as detail:
            raise serializers.ValidationError(detail.messages)


class TrapDjangoValidationErrorUpdateMixin(object):

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as detail:
            raise serializers.ValidationError(detail.messages)
