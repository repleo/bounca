"""API Views for certificate generation"""

import io
import logging
import re
import zipfile

from django.conf import settings
from django.http import Http404, HttpResponse
from django.urls import NoReverseMatch, URLResolver
from django_property_filter import PropertyBooleanFilter, PropertyFilterSet
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from api.mixins import TrapDjangoValidationErrorCreateMixin
from api.serializers import CertificateRevokeSerializer, CertificateSerializer
from x509_pki.models import Certificate, CertificateTypes, KeyStore

if settings.IS_GENERATE_FRONTEND:
    from api import forms  # make sure vuetifyforms can find the classes

    # ignore F401 https://stackoverflow.com/questions/59167405/flake8-ignore-only-f401-rule-in-entire-file
    __all__ = ("forms",)

logger = logging.getLogger(__name__)


class IsCertificateOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj and request.user.id == obj.owner.id:
            return True
        return False


class APIPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class CertificateFilterSet(PropertyFilterSet):
    class Meta:
        model = Certificate
        exclude = ["revoked_uuid"]
        property_fields = [
            ("revoked", PropertyBooleanFilter, ["exact"]),
            ("expired", PropertyBooleanFilter, ["exact"]),
        ]


class CertificateListView(TrapDjangoValidationErrorCreateMixin, ListCreateAPIView):
    model = Certificate
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name", "dn__commonName", "dn__emailAddress", "expires_at"]
    pagination_class = APIPageNumberPagination
    ordering_fields = "__all_related__"
    filterset_class = CertificateFilterSet
    filter_fields = ("type", "parent")

    def get_queryset(self):
        """
        This view should return a list of all the certificates
        for the currently authenticated user.
        """
        user = self.request.user
        return Certificate.objects.filter(owner=user)


class CertificateInstanceView(RetrieveDestroyAPIView):
    model = Certificate
    serializer_class = CertificateSerializer
    queryset = Certificate.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCertificateOwner]

    def get_serializer_class(self):
        if self.request.method.lower() == "delete":
            return CertificateRevokeSerializer
        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance.passphrase_issuer = serializer.validated_data["passphrase_issuer"]
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CertificateInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Certificate.DoesNotExist:
            raise Http404("Certificate not found")
        try:
            info = cert.get_certificate_info()
        except KeyStore.DoesNotExist:
            raise Http404("Certificate has no keystore, " "generation of certificate object went wrong")
        return Response({"text": info})


class ApiRoot(APIView):
    @classmethod
    def as_view(cls, urlpatterns=[], **initkwargs):
        cls.urlpatterns = urlpatterns
        return super().as_view(**initkwargs)

    def get_api_structure(self, patterns, request, *args, **kwargs):
        ret = {}
        for urlpattern in patterns:
            try:
                if isinstance(urlpattern, URLResolver):
                    ret[str(urlpattern.pattern)] = self.get_api_structure(
                        urlpattern.url_patterns, request, *args, **kwargs
                    )
                else:
                    ret[urlpattern.name] = reverse(
                        urlpattern.name, args=args, kwargs=kwargs, request=request, format=kwargs.get("format", None)
                    )
            except NoReverseMatch:
                # Don't bail out if eg. no list routes exist, only detail routes.
                continue
        return ret

    def get(self, request, *args, **kwargs):
        ret = self.get_api_structure(self.urlpatterns, request, *args, **kwargs)
        return Response(ret)


class FileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get_cert_keystore(cert):
        if not hasattr(cert, "keystore") or not cert.keystore.crt or not cert.keystore.key:
            raise KeyStore.DoesNotExist("Certificate has no cert/key, " "something went wrong during generation")
        return {"crt": cert.keystore.crt, "key": cert.keystore.key, "p12": cert.keystore.p12}

    @staticmethod
    def get_crlstore(cert):
        if not hasattr(cert, "crlstore") or not cert.crlstore.crl:
            raise KeyStore.DoesNotExist("Certificate has no crl, " "something went wrong during generation")
        return {"crl": cert.crlstore.crl}


class CertificateFilesView(FileView):
    @classmethod
    def _get_cert_chain(cls, cert):
        return [cert] + cls._get_cert_chain(cert.parent) if cert.parent else [cert]

    @classmethod
    def _get_filename_escape(cls, cert):
        return cert.name.replace(" ", "_")

    @classmethod
    def make_certificate_zip(cls, cert):
        cert_chain = cls._get_cert_chain(cert)
        cert_chain_cert_keys = []
        for _cert in cert_chain:
            try:
                cert_chain_cert_keys.append(cls.get_cert_keystore(_cert))
            except KeyStore.DoesNotExist:
                raise RuntimeError(
                    f"Certificate ({_cert}) has no keystore, " f"generation of certificate object went wrong"
                )

        root_cert_file_content = cert_chain_cert_keys[-1]["crt"]
        intermediate_cert_file_content = cert_chain_cert_keys[1]["crt"]

        cert_chain_file_content = "".join([cert_key["crt"] for cert_key in cert_chain_cert_keys])
        cert_file_content = cert_chain_cert_keys[0]["crt"]
        key_file_content = cert_chain_cert_keys[0]["key"]
        p12_file_content = cert_chain_cert_keys[0]["p12"]

        zipped_file = io.BytesIO()
        with zipfile.ZipFile(zipped_file, "w") as f:
            filename = cls._get_filename_escape(cert)
            f.writestr("rootca.pem", root_cert_file_content)
            f.writestr("intermediate.pem", intermediate_cert_file_content)
            f.writestr("intermediate_root-chain.pem", intermediate_cert_file_content + root_cert_file_content)

            f.writestr(f"{filename}.pem", cert_file_content)
            f.writestr(f"{filename}-chain.pem", cert_chain_file_content)
            f.writestr(f"{filename}.key", key_file_content)

            if p12_file_content:
                f.writestr(f"{filename}.p12", p12_file_content)

        zipped_file.seek(0)
        return zipped_file

    @staticmethod
    def _make_file_response(content, filename):
        response = HttpResponse(content, content_type="application/octet-stream")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    def _make_certificate_content(self, cert):
        label = {
            CertificateTypes.ROOT: "root",
            CertificateTypes.INTERMEDIATE: "intermediate-chain",
            CertificateTypes.SERVER_CERT: "server_cert",
            CertificateTypes.CLIENT_CERT: "client_cert",
            CertificateTypes.OCSP: "ocsp_cert",
        }[cert.type]

        if cert.type is CertificateTypes.ROOT:
            try:
                cert_key = self.get_cert_keystore(cert)
            except KeyStore.DoesNotExist:
                raise RuntimeError("Certificate has no keystore, " "generation of certificate object went wrong")
            filename = f"{self._get_filename_escape(cert)}.{label}.pem"
            return cert_key["crt"], filename

        if cert.type is CertificateTypes.INTERMEDIATE:
            try:
                cert_key = self.get_cert_keystore(cert)
                parent_cert_key = self.get_cert_keystore(cert.parent)
            except KeyStore.DoesNotExist:
                raise RuntimeError("Certificate has no keystore, " "generation of certificate object went wrong")
            filename = f"{self._get_filename_escape(cert)}.{label}.pem"
            return cert_key["crt"] + parent_cert_key["crt"], filename

        if cert.type in [CertificateTypes.SERVER_CERT, CertificateTypes.CLIENT_CERT, CertificateTypes.OCSP]:
            filename = f"{self._get_filename_escape(cert)}.{label}.zip"
            return self.make_certificate_zip(cert), filename

        raise NotImplementedError(f"File generation for cert type {cert.type} " f"not implemented")

    def get(self, request, pk, *args, **kwargs):
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Certificate.DoesNotExist:
            raise Http404("File not found")
        content, filename = self._make_certificate_content(cert)
        return self._make_file_response(content, filename)


class CertificateCRLFilesView(FileView):
    def get(self, request, pk, *args, **kwargs):
        try:
            user = self.request.user
            cert = Certificate.objects.get(pk=pk, owner=user)
        except Certificate.DoesNotExist:
            raise Http404("File not found")

        if cert.type in [CertificateTypes.ROOT, CertificateTypes.INTERMEDIATE]:

            if not cert.crl_distribution_url:
                raise Http404("CRL Distribution is not enabled, " "no crl distribution url")

            try:
                cert_crlstore = self.get_crlstore(cert)
            except KeyStore.DoesNotExist:
                raise Http404("Certificate has no keystore, " "generation of certificate object went wrong")

            matches = re.findall(r"[^\/]+\.crl\.pem$", cert.crl_distribution_url)
            if not matches:
                raise RuntimeError(
                    f"Unexpected wrong format crl distribution url: "
                    f"{cert.crl_distribution_url} should end with "
                    f"<filename>.crl.pem"
                )
            filename = matches[0]
            response = HttpResponse(cert_crlstore["crl"], content_type="application/octet-stream")
            response["Content-Disposition"] = f"attachment; filename={filename}"
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            return response
        else:
            raise ValidationError("CRL can only be generated for Root or Intermediate certificates")
