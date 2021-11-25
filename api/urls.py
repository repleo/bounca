"""API v1 end-points"""

from dj_rest_auth.registration.urls import urlpatterns as urlpatterns_registration
from dj_rest_auth.urls import urlpatterns as urlpatterns_rest_auth
from django.conf.urls import include
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from .views import (
    ApiRoot,
    CertificateCRLFilesView,
    CertificateFilesView,
    CertificateInfoView,
    CertificateInstanceView,
    CertificateListView,
)


class CertificateCrlFileView:
    pass


urlpatterns_apiv1 = [
    path("certificates/files/<int:pk>", CertificateFilesView.as_view(), name="certificate-files"),
    path("certificates/<int:pk>/download", CertificateFilesView.as_view(), name="certificate-download"),
    path("certificates/<int:pk>/crl", CertificateCRLFilesView.as_view(), name="certificate-crl"),
    path("certificates/<int:pk>/info", CertificateInfoView.as_view(), name="certificate-info"),
    path("certificates/<int:pk>", CertificateInstanceView.as_view(), name="certificate-instance"),
    path("certificates", CertificateListView.as_view(), name="certificates"),
    path("auth/", include(urlpatterns_rest_auth)),
    path("auth/registration/", include(urlpatterns_registration)),
]

schema_view = get_swagger_view(title="BounCA API")


urlpatterns = [
    path("v1/", include(urlpatterns_apiv1)),
    path("", ApiRoot.as_view(urlpatterns_apiv1), name="api-root"),
]
