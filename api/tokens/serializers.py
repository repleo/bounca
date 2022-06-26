from rest_framework.serializers import ModelSerializer

from api.models import AuthorisedApp


class AuthorisedAppSerializer(ModelSerializer):
    class Meta:
        fields = ("name", "token", "user")
        read_only_fields = ("token",)
        model = AuthorisedApp
