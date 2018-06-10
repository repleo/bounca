"""Main URL config"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from bounca.api.urls import urlpatterns as urlpatterns_api
from bounca.webapp.urls import urlpatterns as urlpatterns_webapp


urlpatterns = [
    url(r'^api/', include(urlpatterns_api, namespace='api')),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS


    url(r'^', include(urlpatterns_webapp, namespace='bounca')),
]

if settings.DEBUG:
    # admin site is only available if running debug mode
    urlpatterns += url(r'^admin/', include(admin.site.urls)),

urlpatterns += staticfiles_urlpatterns()
