from rest_framework.serializers import ModelSerializer

from api.models import AuthorisedApp


class AuthorisedAppSerializer(ModelSerializer):
    # TODO it is ugly that "user" is visible in the Options of the API.
    #  But not having it as field, will fail the serializer
    #  Solution provided in
    #  https://www.django-rest-framework.org/tutori
    #  al/4-authentication-and-permissions/#associating-snippets-with-users
    #  will not work, as we have a unique constraint for user/name.
    class Meta:
        fields = ("name", "token", "user")
        read_only_fields = ("token",)
        model = AuthorisedApp
        extra_kwargs = {"user": {"required": False}}
