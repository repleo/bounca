"""bounca URL Configuration

"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bounca.api.urls import urlpatterns as urlpatterns_api
from bounca.webapp.urls import urlpatterns as urlpatterns_webapp

urlpatterns = [
    url(r'^api/', include(urlpatterns_api, namespace='api')),
    url(r'^api/docs/', include('rest_framework_docs.urls')), #TODO delete this?
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)), # admin site

    url(r'^', include(urlpatterns_webapp, namespace='bounca')), 
]

urlpatterns += staticfiles_urlpatterns()

