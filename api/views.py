"""API Views for certificate generation"""

import io

import logging
import re
import zipfile
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseBadRequest
from django.views.generic import View, FormView
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response

from api.forms import AddRootCAForm
from api.mixins import TrapDjangoValidationErrorCreateMixin
from api.serializers import CertificateSerializer, CertificateRevokeSerializer
from x509_pki.models import Certificate, CertificateTypes, KeyStore

logger = logging.getLogger(__name__)


class IsCertificateOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj and request.user.id == obj.owner.id:
            return True
        return False

# TODO: BJA throw away?
# class TestFormView(FormView):
#     form_class = AddRootCAForm
#     template_name = "testform.html"


class APIPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class CertificateListView(
        TrapDjangoValidationErrorCreateMixin,
        ListCreateAPIView):
    model = Certificate
    serializer_class = CertificateSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    search_fields = ['name', 'dn__commonName', 'dn__emailAddress', 'expires_at']
    pagination_class = APIPageNumberPagination
    ordering_fields = '__all_related__'
    filter_fields = ('type', 'parent',)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Certificate.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user.id
        return super().create(request, *args, **kwargs)


class CertificateInstanceView(RetrieveDestroyAPIView):
    model = Certificate
    serializer_class = CertificateSerializer
    queryset = Certificate.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsCertificateOwner
    ]

    def get_serializer_class(self):
        if self.request.method.lower() == "delete":
            return CertificateRevokeSerializer
        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance.passphrase_issuer = serializer.validated_data['passphrase_issuer']
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CertificateInfoView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, pk, *args, **kwargs):
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Certificate.DoesNotExist:
            raise Http404("Certificate not found")
        try:
            info = cert.get_certificate_info()
        except KeyStore.DoesNotExist:
            raise Http404("Certificate has no keystore, "
                          "generation of certificate object went wrong")
        return Response({'text': info})


class FileView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @staticmethod
    def get_cert_key(cert):
        if not hasattr(cert, 'keystore') or \
            not cert.keystore.crt or \
                not cert.keystore.key:
            raise KeyStore.DoesNotExist(
                "Certificate has no cert/key, "
                "something went wrong during generation")
        return {'crt': cert.keystore.crt, 'key': cert.keystore.key}

    @staticmethod
    def get_crlstore(cert):
        if not hasattr(cert, 'crlstore') or \
                not cert.crlstore.crl:
            raise KeyStore.DoesNotExist(
                "Certificate has no crl, "
                "something went wrong during generation")
        return {'crl': cert.crlstore.crl}


    @staticmethod
    def read_file(filename):
        with open(filename, 'rb') as f:
            file_content = f.read()
            return file_content

    @classmethod
    def generate_path(cls, certificate):
        prefix_path = ""
        if certificate.parent and certificate.pk != certificate.parent.pk:
            prefix_path = cls.generate_path(certificate.parent)
        return prefix_path + "/" + str(certificate.shortname)

    @classmethod
    def get_root_cert_path(cls, certificate):
        if certificate.parent and certificate.pk != certificate.parent.pk:
            return cls.get_root_cert_path(certificate.parent)
        else:
            root_cert_path = settings.CERTIFICATE_REPO_PATH + "/" + \
                str(certificate.shortname) + "/certs/" + str(certificate.shortname) + ".cert.pem"
            return root_cert_path


class CertificateFilesView(FileView):

    @classmethod
    def _get_cert_chain(cls, cert):
        return  cls._get_cert_chain(cert.parent) + [cert] if cert.parent else [cert]

    @classmethod
    def make_certificate_zip(cls, cert):
        cert_chain = cls._get_cert_chain(cert)
        try:
            cert_chain_cert_keys = [cls.get_cert_key(cert) for cert in cert_chain]
        except KeyStore.DoesNotExist:
            raise Http404("Certificate has no keystore, "
                          "generation of certificate object went wrong")

        root_cert_file_content = cert_chain_cert_keys[0]['crt']
        cert_chain_file_content = "".join([cert_key['crt'] for cert_key in cert_chain_cert_keys])
        cert_file_content = cert_chain_cert_keys[-1]['crt']
        key_file_content = cert_chain_cert_keys[-1]['key']

        zipped_file = io.BytesIO()
        with zipfile.ZipFile(zipped_file, 'w') as f:
            f.writestr("rootca.pem", root_cert_file_content)
            f.writestr(f"{cert.name}.pem", cert_file_content)
            f.writestr(f"{cert.name}-chain.pem", cert_chain_file_content)
            f.writestr(f"{cert.name}.key", key_file_content)
            # f.writestr(f"{cert.name}.p12", p12_file_content) #TODO required?

        zipped_file.seek(0)
        return zipped_file

    def get(self, request, pk, *args, **kwargs):
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Certificate.DoesNotExist:
            raise Http404("File not found")

        if cert.type is CertificateTypes.ROOT:
            try:
                cert_key = self.get_cert_key(cert)
            except KeyStore.DoesNotExist:
                raise Http404("Certificate has no keystore, "
                              "generation of certificate object went wrong")
            filename = f"{cert.name}.pem"
            response = HttpResponse(
                cert_key['crt'], content_type='application/octet-stream')
            response[
                'Content-Disposition'] = f"attachment; filename={filename}"
            response['Access-Control-Expose-Headers'] = "Content-Disposition"
            return response

        if cert.type is CertificateTypes.INTERMEDIATE:
            try:
                cert_key = self.get_cert_key(cert)
                parent_cert_key = self.get_cert_key(cert.parent)
            except KeyStore.DoesNotExist:
                raise Http404("Certificate has no keystore, "
                              "generation of certificate object went wrong")
            filename = f"{cert.name}-chain.pem"
            response = HttpResponse(
                parent_cert_key['crt'] + cert_key['crt'],
                content_type='application/octet-stream')
            response[
                'Content-Disposition'] = f"attachment; filename={filename}"
            response['Access-Control-Expose-Headers'] = "Content-Disposition"
            return response

        if cert.type in [CertificateTypes.SERVER_CERT,
                         CertificateTypes.CLIENT_CERT,
                         CertificateTypes.OCSP]:
            try:
                zipped_file = self.make_certificate_zip(cert)
                name = {CertificateTypes.SERVER_CERT: 'server_cert',
                        CertificateTypes.CLIENT_CERT: 'client_cert',
                        CertificateTypes.OCSP: 'ocsp_cert'}[cert.type]
                filename = f"{cert.name}.{name}.zip"
                response = HttpResponse(zipped_file,
                                        content_type='application/octet-stream')
                response['Content-Disposition'] = (f"attachment; filename={filename}")
                response['Access-Control-Expose-Headers'] = "Content-Disposition"
                return response
            except FileNotFoundError:
                return Http404("File not found")

        return Http404("File not found")


class CertificateCRLFilesView(FileView):

    def get(self, request, pk, *args, **kwargs):
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Certificate.DoesNotExist:
            raise Http404("File not found")

        if cert.type in [CertificateTypes.ROOT,
                         CertificateTypes.INTERMEDIATE]:

            if not cert.crl_distribution_url:
                raise Http404("CRL Distribution is not enabled, "
                              "no crl distribution url")

            try:
                cert_crlstore = self.get_crlstore(cert)
            except KeyStore.DoesNotExist:
                raise Http404("Certificate has no keystore, "
                              "generation of certificate object went wrong")

            matches = re.findall(r"[^\/]+\.crl\.pem$", cert.crl_distribution_url)
            if not matches:
                raise RuntimeError(f"Unexpected wrong format crl distribution url: "
                                   f"{cert.crl_distribution_url} should end with "
                                   f"<filename>.crl.pem")
            filename = matches[0]
            response = HttpResponse(
                cert_crlstore['crl'], content_type='application/octet-stream')
            response[
                'Content-Disposition'] = f"attachment; filename={filename}"
            response['Access-Control-Expose-Headers'] = "Content-Disposition"
            return response
        else:
            raise ValidationError("CRL can only be generated for Root or Intermediate certificates")

# class CertificateCRLFileView(FileView):
#
#     def get(self, request, pk, *args, **kwargs):
#         cert = None
#         user = None
#         try:
#             user = self.request.user
#             cert = Certificate.objects.get(pk=pk, owner=user)
#         except Exception:
#             return HttpResponseNotFound("File not found")
#
#         key_path = settings.CERTIFICATE_REPO_PATH + self.generate_path(cert)
#         if cert.type is CertificateTypes.INTERMEDIATE:
#             orig_file = key_path + "/crl/" + cert.shortname + ".crl.pem"
#             try:
#                 file_content = self.read_file(orig_file)
#                 filename = "%s.crl" % (cert.shortname)
#                 response = HttpResponse(
#                     file_content, content_type='application/octet-stream')
#                 response[
#                     'Content-Disposition'] = ('attachment; filename=%s' % (filename))
#                 return response
#             except FileNotFoundError:
#                 return HttpResponseNotFound("File not found")
#         return HttpResponseNotFound("File not found")


class CertificateOSCPFilesView(FileView):

    def get(self, request, pk, *args, **kwargs):
        return NotImplementedError()
