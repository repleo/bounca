from allauth.account.utils import complete_signup
from allauth.account.views import SignupView
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from superuser_signup.forms import SuperUserSignupForm


class CreateSuperUserView(SignupView):
    form_class = SuperUserSignupForm
    success_url = reverse_lazy("admin:index")

    def dispatch(self, request, *args, **kwargs):
        if User.objects.exists():
            return HttpResponseNotFound()
        return super(SignupView, self).dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        ret = super(CreateSuperUserView, self).get_context_data(**kwargs)
        ret.update({"title": _("Register Super User")})
        return ret

    def form_valid(self, form):
        # no email verification required
        self.user = form.save(self.request)
        try:
            return complete_signup(
                self.request,
                self.user,
                "none",
                self.get_success_url(),
            )
        except ImmediateHttpResponse as e:
            return e.response
