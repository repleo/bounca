from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.shortcuts import redirect
from rest_framework import mixins, serializers, status, exceptions
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from x509_pki.models import Certificate

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'date_joined',
                  'last_login'
        ]

class IsUserOwner(DjangoObjectPermissions):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        pass
        return obj == request.user


class AccountViewSet(
    mixins.DestroyModelMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    """
    A ViewSet for accounts.
    """

    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated, IsUserOwner
    ]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        password = request.data.get("password")
        if not password:
            return Response(
                {"password": ["Password is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        if not user.check_password(password):
            return Response(
                {"password": ["Invalid password."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        super().destroy(request, *args, **kwargs)
        raise exceptions.NotAuthenticated()

    def _delete_certificate(self, certificate):
        for child in Certificate.objects.filter(parent=certificate):
            if child != certificate:
                self._delete_certificate(child)
        certificate.force_delete()

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as e:
            # Manually delete protected related objects
            for related_obj in e.protected_objects:
                if isinstance(related_obj, Certificate):
                    self._delete_certificate(related_obj)
                else:
                    related_obj.delete()
            instance.delete()




