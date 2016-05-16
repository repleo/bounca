from django.conf.urls import patterns, include, url
from .views import CertificateListView
from .views import CertificateInstanceView
from .views import CertificateFilesView

from rest_auth.urls import urlpatterns as urlpatterns_rest_auth
from rest_auth.registration.urls import urlpatterns as urlpatterns_registration

urlpatterns_apiv1 = [
    url(r'^certificates/files/(?P<pk>[\d]+)$', CertificateFilesView.as_view(), name='certificate-files'),

    url(r'^certificates/(?P<pk>[\d]+)$', CertificateInstanceView.as_view(), name='certificate-instance'),
    url(r'^certificates', CertificateListView.as_view(), name='certificates'),


    
    url(r'^auth/', include(urlpatterns_rest_auth)),
    url(r'^auth/registration/', include(urlpatterns_registration))
]


urlpatterns =[
    url(r'^v1/', include(urlpatterns_apiv1, namespace='v1')),  
]
