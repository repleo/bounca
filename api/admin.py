from django.contrib import admin, messages
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth import get_user_model
from django.db import DEFAULT_DB_ALIAS
from django.db.models import ProtectedError
from django.forms import BooleanField, ModelForm

from x509_pki.models import Certificate

from . import utils
from .models import AuthorisedApp

User = get_user_model()


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
    list_display = [
        "user",
        "name",
        "token",
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(AppAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def _delete_certificate(self, certificate):
        for child in Certificate.objects.filter(parent=certificate):
            if child != certificate:
                self._delete_certificate(child)
        certificate.force_delete()

    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ProtectedError as e:
            if request.user.is_superuser:
                # Manually delete protected related objects
                for related_obj in e.protected_objects:
                    if isinstance(related_obj, Certificate):
                        self._delete_certificate(related_obj)
                    else:
                        related_obj.delete()
                obj.delete()
                self.message_user(request, "Superuser override: related objects deleted.", level=messages.WARNING)
            else:
                self.message_user(request, f"Cannot delete: {e}", level=messages.ERROR)

    def get_deleted_objects(self, objs, request):
        """
        Overrides default permission checking for related objects.
        Allows superusers to delete even without explicit related model permissions.
        """
        if request.user.is_superuser:
            collector = NestedObjects(using=DEFAULT_DB_ALIAS)
            collector.collect(objs)
            found_objs = collector.nested()
            found_objs += collector.protected
            return found_objs, [], set(), []
        else:
            return super().get_deleted_objects(objs, request)

    def has_delete_permission(self, request, obj=None):
        # You can also enforce stricter rules here if needed
        return True
