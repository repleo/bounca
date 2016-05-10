



import rest_framework 
from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework import filters

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
        fields = ('id','shortname','name','parent','type','dn','created_at','expires_at','days_valid','revoked','crl_distribution_url','ocsp_distribution_host')
        model = Certificate
        
    def create(self, validated_data):
        dn_data = validated_data.pop('dn')
        dn = DistinguishedName.objects.create(**dn_data)
        certificate = Certificate.objects.create(dn=dn, **validated_data)
        return certificate   


class CertificateList(generics.ListCreateAPIView):
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
    filter_fields = ('type', )


