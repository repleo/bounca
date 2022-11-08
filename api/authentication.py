from functools import wraps

from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication

from api.models import AuthorisedApp

KEYS_TTL = 1800


def cache_value(func):
    @wraps(func)
    def new_func(self, app_token, *args, **kwargs):
        key = f":app_auth:authorised_app:{app_token}:"
        data = cache.get(key)
        if data is None:
            data = func(self, app_token, *args, **kwargs)
            cache.set(key, data, KEYS_TTL)

        return data

    return new_func


class AppTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # The tokens to set: X-AUTH-TOKEN or X-USER-AUTH-TOKEN
        app_token = request.META.get("HTTP_X_AUTH_TOKEN")
        user_token = request.META.get("HTTP_X_USER_AUTH_TOKEN")
        app = self.authorised_app_for_token(app_token)
        if app:
            return app.user, AuthData(app_token, user_token)
        else:
            return None

    # @cache_value
    def authorised_app_for_token(self, app_token):
        return AuthorisedApp.objects.filter(token=app_token).first()


class AuthData(object):
    """
    We store important data connected to the authorisation step in
    this object and we store this object to the request object so
    that the data here can be used through the view and related classes.
    """

    def __init__(self, app_token, user_token):
        self.app_token = app_token
        self.user_token = user_token
