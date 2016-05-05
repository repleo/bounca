"""bounca URL Configuration

"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)), # admin site
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS

]

urlpatterns += staticfiles_urlpatterns()
