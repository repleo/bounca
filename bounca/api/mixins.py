__author__ = "Jeroen Arnoldus"
__copyright__ = "Copyright 2016, Repleo, Amstelveen"
__credits__ = ["Jeroen Arnoldus"]
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Jeroen Arnoldus"
__email__ = "jeroen@repleo.nl"
__status__ = "Production"

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
