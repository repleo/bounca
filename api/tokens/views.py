from copy import deepcopy

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import AuthorisedApp
from api.tokens.serializers import AuthorisedAppSerializer


class AuthorisedAppViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """
    A ViewSet for retrieving tokens.
    """

    serializer_class = AuthorisedAppSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return AuthorisedApp.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = deepcopy(request.data)
        data["user"] = self.request.user.id
        serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
