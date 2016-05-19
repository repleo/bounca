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


admin.site.register(DistinguishedName, X509_pki_DistinguishedNameAdmin)

from .models import Certificate
from .forms import CertificateForm

class X509_pki_CertificateAdmin(admin.ModelAdmin):
    search_fields = ['shortname','name']
    list_display = ('shortname','name','parent','type','dn','created_at','expires_at','days_valid','revoked_at','crl_distribution_url','ocsp_distribution_host')
    form = CertificateForm


    def get_readonly_fields(self, request, obj=None):
        if obj: #This is the case when obj is already created i.e. it's an edit
            return ['shortname','name','parent','type','dn','crl_distribution_url','ocsp_distribution_host','created_at','expires_at','revoked_at']
        else:
            return []

admin.site.register(Certificate, X509_pki_CertificateAdmin)
