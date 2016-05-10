'''
Created on 5 mei 2016

@author: Jeroen Arnoldus
'''

from django import forms
from django.utils import timezone
from .models import DistinguishedName
from .models import Certificate
from .models import CertificateTypes

class DistinguishedNameForm(forms.ModelForm):

    def clean(self):
        """ This is the form's clean method, not a particular field's clean method """
        
        pk = self.instance.pk
        if pk is not None:
            raise forms.ValidationError('Not allowed to update an existing certificate!')
         
    class Meta:
        model = DistinguishedName
        fields = ('commonName','countryName','stateOrProvinceName','localityName','organizationName','organizationalUnitName','emailAddress',)
        
class CertificateForm(forms.ModelForm):

    def clean(self):
        """ This is the form's clean method, not a particular field's clean method """
        cleaned_data = self.cleaned_data
        
        pk = self.instance.pk
        if pk is not None:
            raise forms.ValidationError('Not allowed to update an existing certificate!')

        shortname = cleaned_data.get("shortname")
        cert_type = cleaned_data.get("type")
        dn = cleaned_data.get("dn")

        if Certificate.objects.filter(shortname=shortname, type=cert_type, revoked_at=None).count() > 0:
            raise forms.ValidationError("Shortname (" +shortname+") for " + dict(Certificate.TYPES)[cert_type] + " already exists.")

        if Certificate.objects.filter(dn=dn, type=cert_type, revoked_at=None).count() > 0:
            raise forms.ValidationError("DN (" +str(dn)+") for " + dict(Certificate.TYPES)[cert_type] + " already used.")

        parent = cleaned_data.get("parent")
        if cert_type == CertificateTypes.ROOT and parent: #check_if_root_has_no_parent
            raise forms.ValidationError('Not allowed to have a parent certificate for a ROOT CA certificate')

        if cert_type is not CertificateTypes.ROOT and not parent: #check_if_root_has_no_parent
            raise forms.ValidationError('Non ROOT certificate should have a parent certificate')
        
        if cert_type is CertificateTypes.SERVER_CERT and not parent.type is CertificateTypes.INTERMEDIATE: #check_if_non_root_certificate_has_parent
            raise forms.ValidationError('Server certificate can only be generated for intermediate CA parent')


        if cert_type is CertificateTypes.CLIENT_CERT and not parent.type is CertificateTypes.INTERMEDIATE: #check_if_non_root_certificate_has_parent
            raise forms.ValidationError('Client certificate can only be generated for intermediate CA parent')

        if cert_type is CertificateTypes.SERVER_CERT or cert_type is CertificateTypes.CLIENT_CERT:
            if Certificate.objects.filter(dn=dn, parent=parent, type=CertificateTypes.INTERMEDIATE).count() > 0:
                raise forms.ValidationError("DN (" +str(dn)+") for " + dict(Certificate.TYPES)[cert_type] + "-Certificate already used as intermediate CA.")
             


    
        if cert_type is CertificateTypes.INTERMEDIATE and parent.type is CertificateTypes.ROOT:
            if dn.countryName != parent.dn.countryName:
                raise forms.ValidationError('Country name of Intermediate CA and Root CA should match (policy strict)')
            if dn.stateOrProvinceName != parent.dn.stateOrProvinceName:
                raise forms.ValidationError('State Or Province Name of Intermediate CA and Root CA should match (policy strict)')
            if dn.organizationName != parent.dn.organizationName:
                raise forms.ValidationError('Organization Name of Intermediate CA and Root CA should match (policy strict)')


        if cleaned_data.get('expires_at'):
            now = timezone.now().date()
            expires_at = cleaned_data.get("expires_at")

            days_valid=int((expires_at-now).days)
            if parent and days_valid > parent.days_valid:
                raise forms.ValidationError('Child Certificate expiration data should be before parent expiration date')
              
        return cleaned_data 
    
    class Meta:
        model = Certificate
        fields = ('shortname','name','parent','type','dn','expires_at','crl_distribution_url', 'ocsp_distribution_host' )
