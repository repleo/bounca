"""API v1 end-points"""

from dj_rest_auth.registration.urls import urlpatterns as urlpatterns_registration
from dj_rest_auth.urls import urlpatterns as urlpatterns_rest_auth
from django.conf.urls import include, url
from django.urls import NoReverseMatch, URLResolver
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_swagger.views import get_swagger_view

from .views import (
    CertificateCRLFilesView, CertificateFilesView, CertificateInfoView, CertificateInstanceView, CertificateListView)


class CertificateCrlFileView:
    pass


urlpatterns_apiv1 = [
    url(r'^certificates/files/(?P<pk>[\d]+)$', CertificateFilesView.as_view(), name='certificate-files'),

    url(r'^certificates/(?P<pk>[\d]+)/download$', CertificateFilesView.as_view(),
        name='certificate-download'),
    url(r'^certificates/(?P<pk>[\d]+)/crl$', CertificateCRLFilesView.as_view(),
        name='certificate-crl'),

    url(r'^certificates/(?P<pk>[\d]+)/info$', CertificateInfoView.as_view(), name='certificate-info'),
    url(r'^certificates/(?P<pk>[\d]+)$', CertificateInstanceView.as_view(), name='certificate-instance'),
    url(r'^certificates', CertificateListView.as_view(), name='certificates'),


    url(r'^auth/', include(urlpatterns_rest_auth)),
    url(r'^auth/registration/', include(urlpatterns_registration))
]

schema_view = get_swagger_view(title='BounCA API')


def get_api_structure(patterns, request, *args, **kwargs):
    ret = {}
    for urlpattern in patterns:
        try:
            if isinstance(urlpattern, URLResolver):
                print(urlpattern.pattern)
                ret[str(urlpattern.pattern)] = get_api_structure(urlpattern.url_patterns, request, *args, **kwargs)
            else:
                ret[urlpattern.name] = reverse(
                    urlpattern.name,
                    args=args,
                    kwargs=kwargs,
                    request=request,
                    format=kwargs.get('format', None)
                )
        except NoReverseMatch:
            # Don't bail out if eg. no list routes exist, only detail routes.
            continue
    return ret


@api_view(['GET'])
def api_root(request, *args, **kwargs):
    ret = get_api_structure(urlpatterns_apiv1, request, *args, **kwargs)
    return Response(ret)


urlpatterns = [
    url(r'^v1/', include(urlpatterns_apiv1)),
    url('^', api_root, name='api-root'),
]
