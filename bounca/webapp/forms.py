'''
Created on 15 mei 2016

@author: Jeroen Arnoldus
'''
from django.shortcuts import render

# Create your views here.
from djng.forms import NgModelFormMixin, NgFormValidationMixin
from ..x509_pki.forms import DistinguishedNameForm
from ..x509_pki.forms import CertificateForm
from ..x509_pki.models import CertificateTypes


from djng.forms import NgModelForm

from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django import forms
from django.utils import timezone



class AddDistinguishedNameRootCAForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, DistinguishedNameForm):  
    scope_prefix = 'root_ca_data.dn'
    form_name = 'root_ca_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commonName'].help_text = 'The common name of your certification authority. This field is used to identify your CA in the chain'



class AddRootCAForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, CertificateForm):  
    scope_prefix = 'root_ca_data'
    form_name = 'root_ca_form'

    def clean_parent(self):
        return None

    def clean_type(self):
        return CertificateTypes.ROOT

    def __init__(self, *args, **kwargs):
        kwargs.update(auto_id=False, scope_prefix=self.scope_prefix)
        super().__init__(*args, **kwargs)
        self.fields.pop('dn')
        self.initial['parent'] = None
        self.initial['type'] = CertificateTypes.ROOT
        self.initial['expires_at'] = timezone.now() + timezone.timedelta(weeks=1040)

        self.fields['expires_at'].help_text = 'Expiration date of the root certificate, typically 20 years. (format: yyyy-mm-dd)'


        self.fields['parent'].widget = forms.HiddenInput()
        self.fields['type'].widget = forms.HiddenInput()
        self.fields['passphrase_in'].widget = forms.HiddenInput()
        if 'scope_prefix' in kwargs:
            kwargs.pop('scope_prefix')
        if 'prefix' in kwargs:
            kwargs.pop('prefix')
        self.dn = AddDistinguishedNameRootCAForm(scope_prefix='root_ca_data.dn',**kwargs)


    def get_initial_data(self):
        data = super().get_initial_data()
        data.update({
            self.dn.prefix: self.dn.get_initial_data(),
        })
        return data

    def is_valid(self):
        if not self.dn.is_valid():
            self.errors.update(self.dn.errors)
        return super().is_valid() and self.dn.is_valid()

