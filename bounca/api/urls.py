"""API v1 end-points"""

from django.conf.urls import include, url
from rest_auth.registration.urls import urlpatterns as urlpatterns_registration
from rest_auth.urls import urlpatterns as urlpatterns_rest_auth

from .views import (
    CertificateCRLFileView, CertificateCRLView, CertificateFilesView, CertificateInfoView, CertificateInstanceView,
    CertificateListView, CertificateRevokeView)


urlpatterns_apiv1 = [
    url(r'^certificates/files/(?P<pk>[\d]+)$', CertificateFilesView.as_view(), name='certificate-files'),
    url(r'^certificates/crl/(?P<pk>[\d]+)$', CertificateCRLView.as_view(), name='certificate-crl'),

    url(r'^certificates/crlfile/(?P<pk>[\d]+)$', CertificateCRLFileView.as_view(), name='certificate-crl-file'),

    url(r'^certificates/(?P<pk>[\d]+)$', CertificateInstanceView.as_view(), name='certificate-instance'),
    url(r'^certificates/info/(?P<pk>[\d]+)$', CertificateInfoView.as_view(), name='certificate-info'),
    url(r'^certificates/revoke/(?P<pk>[\d]+)$', CertificateRevokeView.as_view(), name='certificate-revoke'),
    url(r'^certificates', CertificateListView.as_view(), name='certificates'),


    url(r'^auth/', include(urlpatterns_rest_auth)),
    url(r'^auth/registration/', include(urlpatterns_registration))
]


urlpatterns = [
    url(r'^v1/', include(urlpatterns_apiv1, namespace='v1')),
    url(r'docs/', include('rest_framework_swagger.urls', namespace='docs')),
]
