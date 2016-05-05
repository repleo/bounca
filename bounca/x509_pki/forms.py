'''
Created on 5 mei 2016

@author: Jeroen Arnoldus
'''

from django import forms
from .models import DistinguishedName
from .models import Certificate

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

        if Certificate.objects.filter(shortname=shortname, type=cert_type).count() > 0:
            raise forms.ValidationError("Shortname (" +shortname+") for " + dict(Certificate.TYPES)[cert_type] + "-Certificate already exists.")

        parent = cleaned_data.get("parent")
        if cert_type == Certificate.ROOT and parent: #check_if_root_has_no_parent
            raise forms.ValidationError('Not allowed to have a parent certificate for a ROOT CA certificate')

        if cert_type is not Certificate.ROOT and not parent: #check_if_root_has_no_parent
            raise forms.ValidationError('Non ROOT certificate should have a parent certificate')
        return cleaned_data 
    
    class Meta:
        model = Certificate
        fields = ('shortname','name','parent','type','dn')
