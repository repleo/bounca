from django.shortcuts import render


import json
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from .forms import AddRootCAForm

class AddRootCAFormView(FormView):
    template_name = 'bounca/dashboard/forms/add-root-ca.html'
    form_class = AddRootCAForm
    success_url = reverse_lazy('bounca:index') 

from .forms import AddIntermediateCAForm
from ..x509_pki.models import Certificate
from ..x509_pki.models import CertificateTypes

class AddIntermediateCAFormView(FormView):
    template_name = 'bounca/dashboard/forms/add-intermediate-ca.html'
    form_class = AddIntermediateCAForm
    success_url = reverse_lazy('bounca:index') 
    
    def get_initial(self):
        initial = super().get_initial()
        
        if 'parent' not in self.request.GET:
            raise Exception("You should provide the parameter: parent in the url")
        try:
            parent=Certificate.objects.get(pk=self.request.GET['parent'])
        except:
            raise ObjectDoesNotExist("Parent certificate does not exist")
        if parent.type!=CertificateTypes.ROOT and parent.type!=CertificateTypes.INTERMEDIATE:
            raise Exception("Parent certificate type should be root or intermediate")
        initial['parent']=parent.pk;
        initial['dn']={};
        initial['dn']['commonName']=""
        initial['dn']['countryName']=parent.dn.countryName
        initial['dn']['stateOrProvinceName']=parent.dn.stateOrProvinceName
        initial['dn']['localityName']=parent.dn.localityName
        initial['dn']['organizationName']=parent.dn.organizationName
        initial['dn']['organizationalUnitName']=parent.dn.organizationalUnitName
        initial['dn']['emailAddress']=parent.dn.emailAddress
       
        return initial
    
from .forms import AddServerCertificateForm


class AddServerCertificateFormView(FormView):
    template_name = 'bounca/dashboard/forms/add-server-cert.html'
    form_class = AddServerCertificateForm
    success_url = reverse_lazy('bounca:index') 
    
    def get_initial(self):
        initial = super().get_initial()
        
        if 'parent' not in self.request.GET:
            raise Exception("You should provide the parameter: parent in the url")
        try:
            parent=Certificate.objects.get(pk=self.request.GET['parent'])
        except:
            raise ObjectDoesNotExist("Parent certificate does not exist")
#TODO webapp cannot handle the Exception
#        if parent.type!=CertificateTypes.INTERMEDIATE:
#            raise Exception("Parent certificate type should be intermediate")
        initial['parent']=parent.pk;
        initial['dn']={};
        initial['dn']['commonName']=""
        initial['dn']['countryName']=parent.dn.countryName
        initial['dn']['stateOrProvinceName']=parent.dn.stateOrProvinceName
        initial['dn']['localityName']=parent.dn.localityName
        initial['dn']['organizationName']=parent.dn.organizationName
        initial['dn']['organizationalUnitName']=parent.dn.organizationalUnitName
        initial['dn']['emailAddress']=parent.dn.emailAddress
       
        return initial
    
from .forms import AddClientCertificateForm


class AddClientCertificateFormView(FormView):
    template_name = 'bounca/dashboard/forms/add-client-cert.html'
    form_class = AddClientCertificateForm
    success_url = reverse_lazy('bounca:index') 
    
    def get_initial(self):
        initial = super().get_initial()
        
        if 'parent' not in self.request.GET:
            raise Exception("You should provide the parameter: parent in the url")
        try:
            parent=Certificate.objects.get(pk=self.request.GET['parent'])
        except:
            raise ObjectDoesNotExist("Parent certificate does not exist")
#TODO webapp cannot handle the Exception
#        if parent.type!=CertificateTypes.INTERMEDIATE:
#            raise Exception("Parent certificate type should be intermediate")
        initial['parent']=parent.pk;
        initial['dn']={};
        initial['dn']['commonName']=""
        initial['dn']['countryName']=parent.dn.countryName
        initial['dn']['stateOrProvinceName']=parent.dn.stateOrProvinceName
        initial['dn']['localityName']=parent.dn.localityName
        initial['dn']['organizationName']=parent.dn.organizationName
        initial['dn']['organizationalUnitName']=parent.dn.organizationalUnitName
        initial['dn']['emailAddress']=parent.dn.emailAddress
       
        return initial
    
from .forms import CertificateRevokeForm
class CertificateRevokeFormView(FormView):
    template_name = 'bounca/dashboard/forms/revoke-cert.html'
    form_class = CertificateRevokeForm
    success_url = reverse_lazy('bounca:index') 
    

    
    
    
