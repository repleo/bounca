from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings


class PasswordResetSerializerFrontendHost(PasswordResetSerializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    def save(self):
        if "allauth" in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
        else:
            from django.contrib.auth.tokens import default_token_generator

        request = self.context.get("request")
        # Set some values to trigger the send_email method.
        opts = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
            "request": None,  # None triggers to use the host from site object
            "token_generator": default_token_generator,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)
