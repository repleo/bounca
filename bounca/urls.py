"""bounca URL Configuration

"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bounca.api.urls import urlpatterns_apiv1
from bounca.main.urls import urlpatterns as urlpatterns_main

urlpatterns = patterns('',
    url(r'^api/v1/', include(urlpatterns_apiv1)),
    url(r'^api/docs/', include('rest_framework_docs.urls')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)), # admin site

    url(r'^', include(urlpatterns_main)), 
)

urlpatterns += staticfiles_urlpatterns()
