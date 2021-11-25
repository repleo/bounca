"""Admin interface definition for certificates"""
from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets

from .models import Certificate, DistinguishedName, KeyStore


class ReadOnlyAdmin(admin.ModelAdmin):
    """
    ModelAdmin class that prevents modifications through the admin.
    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    Source: https://gist.github.com/aaugustin/1388243
    """

    actions = None

    def get_readonly_fields(self, request, obj=None):
        if self.fieldsets:
            return flatten_fieldsets(self.fieldsets)
        else:
            return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them.
    def has_change_permission(self, request, obj=None):
        return request.method in ["GET", "HEAD"] and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


class X509_pki_DistinguishedNameAdmin(ReadOnlyAdmin):
    search_fields = ["commonName", "organizationName"]
    list_display = (
        "commonName",
        "countryName",
        "stateOrProvinceName",
        "localityName",
        "organizationName",
        "organizationalUnitName",
        "emailAddress",
        "subjectAltNames",
    )


admin.site.register(DistinguishedName, X509_pki_DistinguishedNameAdmin)


class X509_pki_CertificateAdmin(ReadOnlyAdmin):
    search_fields = ["name"]
    list_display = (
        "name",
        "parent",
        "type",
        "dn",
        "created_at",
        "expires_at",
        "days_valid",
        "revoked_at",
        "crl_distribution_url",
        "ocsp_distribution_host",
    )


admin.site.register(Certificate, X509_pki_CertificateAdmin)


class X509_pki_KeyStoreAdmin(ReadOnlyAdmin):
    search_fields = ["certificate__commonName"]
    list_display = ("certificate", "key", "crt")


admin.site.register(KeyStore, X509_pki_KeyStoreAdmin)
