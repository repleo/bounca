"""Main URL config"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from api.urls import urlpatterns as urlpatterns_api
from webapp.urls import urlpatterns as urlpatterns_webapp


urlpatterns = [
    url(r'^api/', include(urlpatterns_api)),
    # TODO fix these URIs, they are dummy for django registration framework.
    url('^', include('django.contrib.auth.urls')),
    url('^account/account_email_verification_sent', TemplateView.as_view(), name='account_email_verification_sent'),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^', include(urlpatterns_webapp)),
]

if settings.DEBUG:
    # admin site is only available if running debug mode
    urlpatterns += url(r'^admin/', admin.site.urls),

urlpatterns += staticfiles_urlpatterns()
