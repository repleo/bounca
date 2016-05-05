from django.contrib import admin

from .models import DistinguishedName
from .forms import DistinguishedNameForm

class X509_pki_DistinguishedNameAdmin(admin.ModelAdmin):
    search_fields = ['commonName','organizationName']
    list_display = ('commonName','countryName','stateOrProvinceName','localityName','organizationName','organizationalUnitName','emailAddress')
    form = DistinguishedNameForm

    def get_readonly_fields(self, request, obj=None):
        if obj: #This is the case when obj is already created i.e. it's an edit
            return ['countryName','stateOrProvinceName','localityName','organizationName','organizationalUnitName','emailAddress','commonName']
        else:
            return []
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(DistinguishedName, X509_pki_DistinguishedNameAdmin)

from .models import Certificate
from .forms import CertificateForm

class X509_pki_DistinguishedAdmin(admin.ModelAdmin):
    search_fields = ['shortname','name']
    list_display = ('shortname','name','parent','type','dn','created_at','expires_at')
    form = CertificateForm

    def get_readonly_fields(self, request, obj=None):
        if obj: #This is the case when obj is already created i.e. it's an edit
            return ['shortname','name','parent','type','dn','created_at','expires_at']
        else:
            return []
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Certificate, X509_pki_DistinguishedAdmin)
