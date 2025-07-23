"""API v1 end-points"""
from dj_rest_auth.registration.urls import urlpatterns as urlpatterns_registration
from dj_rest_auth.urls import urlpatterns as urlpatterns_rest_auth
from django.conf.urls import include
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api.tokens.urls import urlpatterns as urlpatterns_token

from .views import (
    ApiRoot,
    CertificateCRLFilesView,
    CertificateFilesView,
    CertificateInfoView,
    CertificateInstanceView,
    CertificateListView,
    CertificateRenewView,
    NotFoundView,
)


class CertificateCrlFileView:
    pass


urlpatterns_apiv1 = [
    path("certificates/files/<int:pk>", CertificateFilesView.as_view(), name="certificate-files"),
    path("certificates/<int:pk>/download", CertificateFilesView.as_view(), name="certificate-download"),
    path("certificates/<int:pk>/crl", CertificateCRLFilesView.as_view(), name="certificate-crl"),
    path("certificates/<int:pk>/info", CertificateInfoView.as_view(), name="certificate-info"),
    path("certificates/<int:pk>/renew", CertificateRenewView.as_view(), name="certificate-renew"),
    path("certificates/<int:pk>", CertificateInstanceView.as_view(), name="certificate-instance"),
    path("certificates", CertificateListView.as_view(), name="certificates"),
    path("auth/", include(urlpatterns_token)),
    path("auth/", include(urlpatterns_rest_auth)),
    path(
        "auth/registration/account-email-verification-sent/",
        NotFoundView.as_view(),
        name="account_email_verification_sent",
    ),
    path("auth/registration/", include(urlpatterns_registration)),
]


schema_view = get_schema_view(
   openapi.Info(
      title="BounCA API",
      default_version='v1',
      description="API documentation",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("v1/", include(urlpatterns_apiv1)),
    path("", ApiRoot.as_view(urlpatterns_apiv1), name="api-root"),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    # TDOD BJA zet deze in footer of andere docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
