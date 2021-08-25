"""API v1 end-points"""

from django.conf.urls import include, url
from dj_rest_auth.registration.urls import urlpatterns as urlpatterns_registration
from dj_rest_auth.urls import urlpatterns as urlpatterns_rest_auth
from rest_framework_swagger.views import get_swagger_view

from .views import (
    CertificateCRLFileView, CertificateCRLView, CertificateFilesView, CertificateInfoView,
    CertificateInstanceView,
    CertificateListView, CertificateRevokeView, TestFormView)


urlpatterns_apiv1 = [
    url(r'^certificates/files/(?P<pk>[\d]+)$', CertificateFilesView.as_view(), name='certificate-files'),
    url(r'^certificates/crl/(?P<pk>[\d]+)$', CertificateCRLView.as_view(), name='certificate-crl'),

    url(r'^certificates/crlfile/(?P<pk>[\d]+)$', CertificateCRLFileView.as_view(), name='certificate-crl-file'),

    url(r'^certificates/(?P<pk>[\d]+)/info$', CertificateInfoView.as_view(),
        name='certificate-info'),
    url(r'^certificates/(?P<pk>[\d]+)$', CertificateInstanceView.as_view(), name='certificate-instance'),
    # url(r'^certificates/(?P<pk>[\d]+)/revoke$', CertificateRevokeView.as_view(), name='certificate-revoke'),
    url(r'^certificates', CertificateListView.as_view(), name='certificates'),


    url(r'^auth/', include(urlpatterns_rest_auth)),
    url(r'^auth/registration/$', include(urlpatterns_registration))
]

schema_view = get_swagger_view(title='BounCA API')

urlpatterns = [
    url(r'testform/', TestFormView.as_view()),
    url(r'^v1/', include(urlpatterns_apiv1)),
    url(r'docs/', schema_view),
]
