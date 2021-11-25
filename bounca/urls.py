"""Main URL config"""
from dj_rest_auth.registration.views import VerifyEmailView
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.generic import TemplateView

from api.urls import urlpatterns as urlpatterns_api

urlpatterns = [
    # these urls are used to generate email content
    path("auth/password-reset/confirm/<uidb64>/<token>", TemplateView.as_view(), name="password_reset_confirm"),
    path("auth/login/", VerifyEmailView.as_view(), name="account_email_verification_sent"),
    path("api/", include(urlpatterns_api)),
    path("auth/", include("rest_framework.urls")),
    path("auth/account-confirm-email/<key>", TemplateView.as_view(), name="account_confirm_email"),
]

if settings.ADMIN:
    urlpatterns += [
        path("admin/", admin.site.urls),
        path("grappelli/", include("grappelli.urls")),  # grappelli URLS
    ]


urlpatterns += staticfiles_urlpatterns()
