from django.contrib import admin

from bounca.x509_pki.models import DistinguishedName

class X509_pki_DistinguishedNameAdmin(admin.ModelAdmin):
    search_fields = ['commonName','organizationName']
    list_display = ('commonName','countryName','stateOrProvinceName','localityName','organizationName','organizationalUnitName','emailAddress')
admin.site.register(DistinguishedName, X509_pki_DistinguishedNameAdmin)

from bounca.x509_pki.models import Certificate
class X509_pki_DistinguishedAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name','parent','type','dn')
admin.site.register(Certificate, X509_pki_DistinguishedAdmin)
