



import rest_framework 
from rest_framework import generics, permissions
from rest_framework import serializers

class APIPageNumberPagination(rest_framework.pagination.PageNumberPagination):
    page_size=20

from ..x509_pki.models import DistinguishedName

class DistinguishedNameSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('commonName','countryName','stateOrProvinceName','localityName','organizationName','organizationalUnitName','emailAddress')
        model = DistinguishedName

from ..x509_pki.models import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    dn = DistinguishedNameSerializer()

    class Meta:
        fields = ('shortname','name','parent','type','dn','created_at','expires_at','days_valid','revoked_at','crl_distribution_url','ocsp_distribution_host')
        model = Certificate
        
    


class CertificateList(generics.ListAPIView):
    model = Certificate
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [
        permissions.AllowAny
    ]
    search_fields = ('shortname','name',) 
    pagination_class = APIPageNumberPagination


