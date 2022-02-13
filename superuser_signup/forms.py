from allauth.account.forms import SignupForm


class SuperUserSignupForm(SignupForm):
    def save(self, request):
        user = super(SuperUserSignupForm, self).save(request)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
