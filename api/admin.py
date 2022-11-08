from django.contrib import admin
from django.forms import BooleanField, ModelForm

from . import utils
from .models import AuthorisedApp


class AuthorisedAppForm(ModelForm):
    generate_new_token = BooleanField(required=False, initial=False)

    class Meta:
        model = AuthorisedApp
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AuthorisedAppForm, self).__init__(*args, **kwargs)
        self.fields["token"].disabled = not self.current_user.is_superuser
        self.fields["token"].required = False

    def clean(self):
        if self.cleaned_data.get("generate_new_token", False):
            self.cleaned_data["token"] = utils.new_token(44)
        return self.cleaned_data

    def save(self, commit=True):
        obj = super(AuthorisedAppForm, self).save(commit=False)
        obj.save(commit)
        if commit:
            obj.save()
            obj.save_m2m()
        return obj


@admin.register(AuthorisedApp)
class AppAdmin(admin.ModelAdmin):
    form = AuthorisedAppForm
    list_display = ("name", "token")

    def get_form(self, request, obj=None, **kwargs):
        form = super(AppAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
