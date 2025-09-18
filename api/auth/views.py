from copy import deepcopy

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import AuthorisedApp
from api.tokens.serializers import AuthorisedAppSerializer
from api.views import APIPageNumberPagination


class AccountViewSet(
    mixins.DestroyModelMixin, GenericViewSet
):
    """
    A ViewSet for accounts.
    """

    serializer_class = AuthorisedAppSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return User.objects.filter(user=self.request.user)


