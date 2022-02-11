"""Serializers for Certificate API"""

import django_countries
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import password_validation
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from certificate_engine.types import CertificateTypes
from x509_pki.models import Certificate, DistinguishedName, KeyStore

countries = django_countries.Countries()


class DistinguishedNameSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        fields = (
            "commonName",
            "countryName",
            "stateOrProvinceName",
            "localityName",
            "organizationName",
            "organizationalUnitName",
            "emailAddress",
            "subjectAltNames",
        )
        model = DistinguishedName


class CertificateSerializer(serializers.ModelSerializer):
    dn = DistinguishedNameSerializer()
    passphrase_issuer = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    passphrase_out = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    passphrase_out_confirmation = serializers.CharField(
        max_length=200, required=False, allow_null=True, allow_blank=True
    )

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = (
            "id",
            "name",
            "owner",
            "parent",
            "type",
            "dn",
            "created_at",
            "expires_at",
            "revoked_at",
            "days_valid",
            "expired",
            "revoked",
            "crl_distribution_url",
            "ocsp_distribution_host",
            "passphrase_issuer",
            "passphrase_out",
            "passphrase_out_confirmation",
        )
        model = Certificate
        extra_kwargs = {
            "passphrase_out": {"write_only": True},
            "passphrase_out_confirmation": {"write_only": True},
            "passphrase_issuer": {"write_only": True},
        }

    def validate_passphrase_out(self, passphrase_out):
        if passphrase_out:
            password_validation.validate_password(passphrase_out, self.instance)
            return passphrase_out
        return None

    def validate_passphrase_issuer(self, passphrase_issuer):
        if passphrase_issuer:
            if not self.initial_data.get("parent"):
                raise serializers.ValidationError(
                    "You should provide a parent certificate if you provide an issuer passphrase"
                )
            parent = Certificate.objects.get(pk=self.initial_data.get("parent"))
            try:
                if not parent.is_passphrase_valid(passphrase_issuer):
                    raise serializers.ValidationError("Passphrase incorrect. Not allowed " "to revoke your certificate")
            except KeyStore.DoesNotExist:
                raise serializers.ValidationError("Certificate has no cert, something went " "wrong during generation")
            return passphrase_issuer
        return None

    def validate_passphrase_out_confirmation(self, passphrase_out_confirmation):
        if passphrase_out_confirmation:
            passphrase_out = self.initial_data.get("passphrase_out")
            if passphrase_out and passphrase_out_confirmation and passphrase_out != passphrase_out_confirmation:
                raise serializers.ValidationError("The two passphrase fields didn't match.")
            password_validation.validate_password(passphrase_out_confirmation, self.instance)
            return passphrase_out_confirmation
        return None

    def validate(self, data):
        name = data.get("name")
        if not name:
            name = str(data.get("dn").get("commonName"))
        cert_type = data.get("type")
        owner = data.get("owner")

        if Certificate.objects.filter(name=name, owner=owner, type=cert_type).count() > 0:
            raise serializers.ValidationError(f"{dict(Certificate.TYPES)[cert_type]} " f'"{name}" already exists.')

        return data

    def create(self, validated_data):
        dn_data = validated_data.pop("dn")
        dn = DistinguishedName.objects.create(**dn_data)
        certificate = Certificate.objects.create(dn=dn, **validated_data)
        return certificate


class CertificateRevokeSerializer(serializers.ModelSerializer):
    passphrase_issuer = serializers.CharField(max_length=200, required=True)

    class Meta:
        fields = ("passphrase_issuer",)
        model = Certificate
        extra_kwargs = {"passphrase_issuer": {"write_only": True}}

    def validate_passphrase_issuer(self, passphrase_issuer):
        if passphrase_issuer:
            if self.instance.type == CertificateTypes.ROOT:
                revoke_issuer = self.instance
            else:
                revoke_issuer = self.instance.parent
            try:
                if not revoke_issuer.is_passphrase_valid(passphrase_issuer):
                    raise serializers.ValidationError("Passphrase incorrect. Not allowed " "to revoke your certificate")
            except KeyStore.DoesNotExist:
                raise serializers.ValidationError("Certificate has no cert, something went " "wrong during generation")
            return passphrase_issuer
        return None


class CertificateCRLSerializer(serializers.ModelSerializer):
    passphrase_issuer = serializers.CharField(max_length=200, required=True)

    class Meta:
        fields = ("passphrase_issuer",)
        model = Certificate
        extra_kwargs = {"passphrase_issuer": {"write_only": True}}

    def validate_passphrase_issuer(self, passphrase_issuer):
        if passphrase_issuer:
            self.instance.passphrase_issuer = passphrase_issuer
            if not self.instance.is_passphrase_valid():
                raise serializers.ValidationError("Passphrase issuer incorrect. No permission to create CRL File")
            return passphrase_issuer
        return None

    def update(self, instance, validated_data):
        instance.passphrase_issuer = validated_data["passphrase_issuer"]
        instance.generate_crl()
        return instance


class UserSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = ("username", "email", "first_name", "last_name")
        read_only_fields = ("username",)
