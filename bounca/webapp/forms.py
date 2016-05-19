'''
Created on 15 mei 2016

@author: Jeroen Arnoldus
'''

# Create your views here.
from djng.forms import NgModelFormMixin, NgFormValidationMixin
from ..x509_pki.forms import DistinguishedNameForm
from ..x509_pki.forms import CertificateForm
from ..x509_pki.forms import CertificateRevokeForm
from ..x509_pki.models import CertificateTypes


from djng.forms import NgModelForm

from djng.styling.bootstrap3.forms import Bootstrap3FormMixin
from django import forms
from django.utils import timezone



class AddDistinguishedNameRootCAForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, DistinguishedNameForm):  
    scope_prefix = 'cert_data.dn'
    form_name = 'cert_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commonName'].help_text = 'The common name of your certification authority. This field is used to identify your CA in the chain'



class AddRootCAForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, CertificateForm):  
    scope_prefix = 'cert_data'
    form_name = 'cert_form'

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
        if 'initial' in kwargs and 'dn' in kwargs['initial']:
            initial = kwargs.pop('initial')
            kwargs['initial']= initial['dn']
        self.dn = AddDistinguishedNameRootCAForm(scope_prefix='cert_data.dn',**kwargs)


    def is_valid(self):
        if not self.dn.is_valid():
            self.errors.update(self.dn.errors)
        return super().is_valid() and self.dn.is_valid()


class AddDistinguishedNameIntermediateCAForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, DistinguishedNameForm):  
    scope_prefix = 'cert_data.dn'
    form_name = 'cert_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['countryName'].widget = forms.ChoiceField(widget=forms.RadioSelect(attrs={'disabled': 'disabled'}))

        self.fields['commonName'].help_text = 'The common name of your intermediate certification authority. This field is used to identify your intermediate CA in the chain'
        self.fields['countryName'].widget.attrs['disabled'] = 'disabled'
        self.fields['stateOrProvinceName'].widget.attrs['readonly'] = True
        self.fields['organizationName'].widget.attrs['readonly'] = True
        self.fields['localityName'].widget.attrs['readonly'] = True
        

class AddIntermediateCAForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, CertificateForm):  
    scope_prefix = 'cert_data'
    form_name = 'cert_form'

    def clean_parent(self):
        return None

    def clean_type(self):
        return CertificateTypes.INTERMEDIATE

    def __init__(self, *args, **kwargs):
        kwargs.update(auto_id=False, scope_prefix=self.scope_prefix)
        super().__init__(*args, **kwargs)
        self.fields.pop('dn')
        self.initial['type'] = CertificateTypes.INTERMEDIATE
        self.initial['expires_at'] = timezone.now() + timezone.timedelta(weeks=520)

        self.fields['expires_at'].help_text = 'Expiration date of the intermediate certificate, typically 10 years. (format: yyyy-mm-dd)'


        self.fields['parent'].widget = forms.HiddenInput()
        self.fields['type'].widget = forms.HiddenInput()
        self.fields['crl_distribution_url'].widget = forms.HiddenInput()
        self.fields['ocsp_distribution_host'].widget = forms.HiddenInput()

        if 'scope_prefix' in kwargs:
            kwargs.pop('scope_prefix')
        if 'prefix' in kwargs:
            kwargs.pop('prefix')
        if 'initial' in kwargs and 'dn' in kwargs['initial']:
            initial = kwargs.pop('initial')
            kwargs['initial']= initial['dn']
        self.dn = AddDistinguishedNameIntermediateCAForm(scope_prefix='cert_data.dn',**kwargs)


    def is_valid(self):
        if not self.dn.is_valid():
            self.errors.update(self.dn.errors)
        return super().is_valid() and self.dn.is_valid()


class AddDistinguishedNameServerCertificateForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, DistinguishedNameForm):  
    scope_prefix = 'cert_data.dn'
    form_name = 'cert_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commonName'].help_text = 'The fully qualified domain name (FQDN) of your server. This must match exactly what the url or wildcard or a name mismatch error will occur.'


class AddServerCertificateForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, CertificateForm):  
    scope_prefix = 'cert_data'
    form_name = 'cert_form'

    def clean_parent(self):
        return None

    def clean_type(self):
        return CertificateTypes.SERVER_CERT

    def __init__(self, *args, **kwargs):
        kwargs.update(auto_id=False, scope_prefix=self.scope_prefix)
        super().__init__(*args, **kwargs)
        self.fields.pop('dn')
        self.initial['type'] = CertificateTypes.SERVER_CERT
        self.initial['expires_at'] = timezone.now() + timezone.timedelta(weeks=52)
        self.initial['passphrase_out'] = ""
        self.initial['passphrase_out_confirmation'] = ""
        self.fields['expires_at'].help_text = 'Expiration date of the server certificate, typically 1 year. (format: yyyy-mm-dd)'


        self.fields['parent'].widget = forms.HiddenInput()
        self.fields['type'].widget = forms.HiddenInput()
        self.fields['crl_distribution_url'].widget = forms.HiddenInput()
        self.fields['ocsp_distribution_host'].widget = forms.HiddenInput()

        self.fields['passphrase_out'].required = False
        self.fields['passphrase_out_confirmation'].required = False


        if 'scope_prefix' in kwargs:
            kwargs.pop('scope_prefix')
        if 'prefix' in kwargs:
            kwargs.pop('prefix')
        if 'initial' in kwargs and 'dn' in kwargs['initial']:
            initial = kwargs.pop('initial')
            kwargs['initial']= initial['dn']
        self.dn = AddDistinguishedNameServerCertificateForm(scope_prefix='cert_data.dn',**kwargs)


    def is_valid(self):
        if not self.dn.is_valid():
            self.errors.update(self.dn.errors)
        return super().is_valid() and self.dn.is_valid()

class AddDistinguishedNameClientCertificateForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, DistinguishedNameForm):  
    scope_prefix = 'cert_data.dn'
    form_name = 'cert_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commonName'].help_text = 'The account name of the client, for example username or email.'


class AddClientCertificateForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, CertificateForm):  
    scope_prefix = 'cert_data'
    form_name = 'cert_form'

    def clean_parent(self):
        return None

    def clean_type(self):
        return CertificateTypes.CLIENT_CERT

    def __init__(self, *args, **kwargs):
        kwargs.update(auto_id=False, scope_prefix=self.scope_prefix)
        super().__init__(*args, **kwargs)
        self.fields.pop('dn')
        self.initial['type'] = CertificateTypes.CLIENT_CERT
        self.initial['expires_at'] = timezone.now() + timezone.timedelta(weeks=52)
        self.initial['passphrase_out'] = ""
        self.initial['passphrase_out_confirmation'] = ""
        self.fields['expires_at'].help_text = 'Expiration date of the client certificate, typically 1 year. (format: yyyy-mm-dd)'


        self.fields['parent'].widget = forms.HiddenInput()
        self.fields['type'].widget = forms.HiddenInput()
        self.fields['crl_distribution_url'].widget = forms.HiddenInput()
        self.fields['ocsp_distribution_host'].widget = forms.HiddenInput()

        self.fields['passphrase_out'].required = False
        self.fields['passphrase_out_confirmation'].required = False
        
        
        if 'scope_prefix' in kwargs:
            kwargs.pop('scope_prefix')
        if 'prefix' in kwargs:
            kwargs.pop('prefix')
        if 'initial' in kwargs and 'dn' in kwargs['initial']:
            initial = kwargs.pop('initial')
            kwargs['initial']= initial['dn']
        self.dn = AddDistinguishedNameClientCertificateForm(scope_prefix='cert_data.dn',**kwargs)


    def is_valid(self):
        if not self.dn.is_valid():
            self.errors.update(self.dn.errors)
        return super().is_valid() and self.dn.is_valid()
    

class CertificateRevokeForm(  NgModelFormMixin, NgFormValidationMixin, Bootstrap3FormMixin, NgModelForm, CertificateRevokeForm):  
    scope_prefix = 'cert_data'
    form_name = 'cert_form'

    def clean_parent(self):
        return None


    def __init__(self, *args, **kwargs):
        kwargs.update(auto_id=False, scope_prefix=self.scope_prefix)
        super().__init__(*args, **kwargs)
