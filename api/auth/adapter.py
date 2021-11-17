from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri
from rest_framework.reverse import reverse


class DefaultAccountAdapterFrontendHost(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        ret = build_absolute_uri(None, url)
        return ret
