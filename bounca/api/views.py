


import rest_framework
from rest_framework import generics, permissions
from .serializers import CertificateSerializer
from ..x509_pki.models import Certificate
from .mixins import TrapDjangoValidationErrorCreateMixin

class APIPageNumberPagination(rest_framework.pagination.PageNumberPagination):
    page_size=10

class CertificateListView(TrapDjangoValidationErrorCreateMixin, generics.ListCreateAPIView):
    model = Certificate
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [
#        permissions.DjangoObjectPermissions
#
# Django Guardian configure
        permissions.IsAuthenticated
    ]
    search_fields = ('shortname','name',) 
    pagination_class = APIPageNumberPagination
    filter_fields = ('type', 'parent',)

class CertificateInstanceView(generics.RetrieveAPIView):
    model = Certificate
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [
#        permissions.DjangoObjectPermissions
#
# Django Guardian configure
        permissions.IsAuthenticated
    ]

