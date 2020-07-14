"""API Views for certificate generation"""

import io
import logging
import zipfile

import rest_framework
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import View
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from x509_pki.models import Certificate, CertificateTypes
from api.mixins import TrapDjangoValidationErrorCreateMixin
from api.serializers import CertificateCRLSerializer, CertificateRevokeSerializer, CertificateSerializer


logger = logging.getLogger(__name__)


class APIPageNumberPagination(PageNumberPagination):
    page_size = 10


class CertificateListView(
        TrapDjangoValidationErrorCreateMixin,
        generics.ListCreateAPIView):
    model = Certificate
    serializer_class = CertificateSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    search_fields = ('shortname', 'name',)
    pagination_class = APIPageNumberPagination
    filter_fields = ('type', 'parent',)

    def get(self, request, *args, **kwargs):
        return generics.ListCreateAPIView.get(self, request, *args, **kwargs)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Certificate.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user.id
        return generics.ListCreateAPIView.create(
            self, request, *args, **kwargs)


class CertificateInstanceView(generics.RetrieveAPIView):
    model = Certificate
    serializer_class = CertificateSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        user = self.request.user
        return Certificate.objects.filter(owner=user)


class IsCertificateOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj and request.user.id == obj.owner.id:
            return True
        return False


class CertificateRevokeView(generics.UpdateAPIView):
    model = Certificate
    serializer_class = CertificateRevokeSerializer
    queryset = Certificate.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsCertificateOwner
    ]


class CertificateCRLView(generics.UpdateAPIView):
    model = Certificate
    serializer_class = CertificateCRLSerializer
    queryset = Certificate.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsCertificateOwner
    ]


class CertificateInfoView(View):

    def get(self, request, pk, *args, **kwargs):
        cert = None
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Exception:
            return HttpResponseNotFound("File not found")
        info = cert.get_certificate_info()
        return HttpResponse(info)


class FileView(View):

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


class CertificateCRLFileView(FileView):

    def get(self, request, pk, *args, **kwargs):
        cert = None
        user = None
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Exception:
            return HttpResponseNotFound("File not found")

        key_path = settings.CERTIFICATE_REPO_PATH + self.generate_path(cert)
        if cert.type is CertificateTypes.INTERMEDIATE:
            orig_file = key_path + "/crl/" + cert.shortname + ".crl.pem"
            try:
                file_content = self.read_file(orig_file)
                filename = "%s.crl" % (cert.shortname)
                response = HttpResponse(
                    file_content, content_type='application/octet-stream')
                response[
                    'Content-Disposition'] = ('attachment; filename=%s' % (filename))
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")
        return HttpResponseNotFound("File not found")


class CertificateFilesView(FileView):

    @classmethod
    def make_certificate_zip_response(cls, key_path, cert, cert_type):
        root_cert_file = cls.get_root_cert_path(cert)
        root_cert_file_content = cls.read_file(root_cert_file)
        cert_chain_file = key_path + "/certs/" + cert_type + \
            "/" + cert.shortname + "-chain.cert.pem"
        cert_chain_file_content = cls.read_file(cert_chain_file)
        cert_file = key_path + "/certs/" + cert_type + "/" + cert.shortname + ".cert.pem"
        cert_file_content = cls.read_file(cert_file)
        csr_file = key_path + "/csr/" + cert_type + "/" + cert.shortname + ".csr.pem"
        csr_file_content = cls.read_file(csr_file)
        key_file = key_path + "/private/" + cert_type + "/" + cert.shortname + ".key.pem"
        key_file_content = cls.read_file(key_file)
        p12_file = key_path + "/private/" + cert_type + "/" + cert.shortname + ".p12"
        p12_file_content = cls.read_file(p12_file)

        zipped_file = io.BytesIO()
        with zipfile.ZipFile(zipped_file, 'w') as f:
            f.writestr("rootca.pem", root_cert_file_content)
            f.writestr(cert.shortname + ".csr", csr_file_content)
            f.writestr(cert.shortname + ".pem", cert_file_content)
            f.writestr(cert.shortname + "-chain.pem", cert_chain_file_content)
            f.writestr(cert.shortname + ".key", key_file_content)
            f.writestr(cert.shortname + ".p12", p12_file_content)

        zipped_file.seek(0)

        filename = "%s.server_cert.zip" % (cert.shortname)
        response = HttpResponse(zipped_file,
                                content_type='application/octet-stream')
        response[
            'Content-Disposition'] = ('attachment; filename=%s' % (filename))
        return response

    def get(self, request, pk, *args, **kwargs):
        cert = None
        user = None
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Exception:
            return HttpResponseNotFound("File not found")

        key_path = settings.CERTIFICATE_REPO_PATH + self.generate_path(cert)
        if cert.type is CertificateTypes.ROOT:
            orig_file = key_path + "/certs/" + cert.shortname + ".cert.pem"
            try:
                file_content = self.read_file(orig_file)
                filename = "%s.pem" % (cert.shortname)
                response = HttpResponse(
                    file_content, content_type='application/octet-stream')
                response[
                    'Content-Disposition'] = ('attachment; filename=%s' % (filename))
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")

        if cert.type is CertificateTypes.INTERMEDIATE:
            orig_file = key_path + "/certs/" + cert.shortname + "-chain.cert.pem"
            try:
                file_content = self.read_file(orig_file)
                filename = "%s-chain.pem" % (cert.shortname)
                response = HttpResponse(
                    file_content, content_type='application/octet-stream')
                response[
                    'Content-Disposition'] = ('attachment; filename=%s' % (filename))
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")

        key_path = settings.CERTIFICATE_REPO_PATH + self.generate_path(cert.parent)

        if cert.type is CertificateTypes.SERVER_CERT:
            try:
                response = self.make_certificate_zip_response(
                    key_path, cert, "server_cert")
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")

        if cert.type is CertificateTypes.CLIENT_CERT:
            try:
                response = self.make_certificate_zip_response(
                    key_path, cert, "usr_cert")
                return response
            except FileNotFoundError:
                return HttpResponseNotFound("File not found")
        return HttpResponseNotFound("File not found")
