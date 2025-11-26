"""Models for storing subject and certificate information"""

import datetime
import uuid

import pytz
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone
from django_countries.fields import CountryField

from bounca import settings
from certificate_engine.ssl.certificate import Certificate as CertificateGenerator
from certificate_engine.ssl.crl import revocation_list_builder, serialize
from certificate_engine.ssl.info import get_certificate_fingerprint, get_certificate_info
from certificate_engine.ssl.key import Key as KeyGenerator
from certificate_engine.types import CertificateTypes

User = get_user_model()


class DistinguishedName(models.Model):
    alphanumeric_validator = RegexValidator(
        r"^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ \*]*$", "Only alphanumeric characters and [@#$%^&+=_,-.] are allowed."
    )
    country_validator = RegexValidator(
        r"^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ \*]*$", "Only alphanumeric characters and [@#$%^&+=_,-.] are allowed."
    )

    countryName = CountryField(
        "Country", help_text="The two-character country name in ISO 3166 format.", blank=True, null=True
    )
    stateOrProvinceName = models.CharField(
        "State or Province Name",
        max_length=128,
        validators=[alphanumeric_validator],
        help_text="The state/region where your organization is located. "
        "This shouldn't be abbreviated. (1–128 characters)",
        blank=True,
        null=True,
    )
    localityName = models.CharField(
        "Locality Name",
        max_length=128,
        validators=[alphanumeric_validator],
        help_text="The city where your organization is located. (1–128 characters)",
        blank=True,
        null=True,
    )
    organizationName = models.CharField(
        "Organization Name",
        max_length=64,
        validators=[alphanumeric_validator],
        help_text="The legal name of your organization. This should not be abbreviated and should include "
        "suffixes such as Inc, Corp, or LLC.",
        blank=True,
        null=True,
    )
    organizationalUnitName = models.CharField(
        "Organization Unit Name",
        max_length=64,
        validators=[alphanumeric_validator],
        help_text="The division of your organization handling the certificate.",
        blank=True,
        null=True,
    )
    emailAddress = models.EmailField(
        "Email Address",
        max_length=64,
        validators=[alphanumeric_validator],
        help_text="The email address to contact your organization.",
        blank=True,
        null=True,
    )
    commonName = models.CharField(
        "Common Name",
        max_length=64,
        validators=[alphanumeric_validator],
        help_text="The fully qualified domain name (FQDN) of your server. This must match "
        "exactly what you type in your web browser or you will receive a name mi"
        "smatch error.",
    )
    subjectAltNames = ArrayField(
        models.CharField(max_length=64, validators=[alphanumeric_validator]),
        help_text="subjectAltName list, i.e. dns names for server certs and email adresses "
        "for client certs. (separate by comma)",
        blank=True,
        null=True,
    )

    def _to_dn(self, email_label="EMAIL"):
        dn = []
        if self.commonName is not None:
            dn.append("CN={}".format(self.commonName))
        if self.organizationName is not None:
            dn.append("O={}".format(self.organizationName))
        if self.organizationalUnitName is not None:
            dn.append("OU={}".format(self.organizationalUnitName))
        if self.localityName is not None:
            dn.append("L={}".format(self.localityName))
        if self.stateOrProvinceName is not None:
            dn.append("ST={}".format(self.stateOrProvinceName))
        if self.emailAddress is not None:
            dn.append("{}={}".format(email_label, self.emailAddress))
        if self.countryName is not None:
            dn.append("C={}".format(self.countryName))
        return dn

    @property
    def dn(self):
        return ", ".join(self._to_dn(email_label="EMAIL"))

    @property
    def subj(self):
        return "/".join([""] + self._to_dn(email_label="emailAddress"))

    # Create only model
    def save(self, *args, **kwargs):
        if self.id is None:
            self.full_clean()
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Not allowed to update a DistinguishedName record")

    @property
    def slug_commonName(self):
        return slugify(self.commonName)

    def __unicode__(self):
        return str(f"{self.id}-{self.commonName}")

    def __str__(self):
        return str(f"{self.id}-{self.commonName}")


def validate_in_future(value):
    if value <= timezone.now().date():
        raise ValidationError(f"{value} is not in the future!")


class CertificateQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete()


class Certificate(models.Model):
    objects = CertificateQuerySet.as_manager()
    alphanumeric = RegexValidator(
        r"^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ ]*$", "Only alphanumeric characters and [@#$%^&+=_,-.] are allowed."
    )

    crl_url_validator = RegexValidator(r"[^\/]\.crl$", "CRL url should end with <filename>.crl")

    TYPES = (
        (CertificateTypes.ROOT, "Root CA Certificate"),
        (CertificateTypes.INTERMEDIATE, "Intermediate CA Certificate"),
        (CertificateTypes.SERVER_CERT, "Server Certificate"),
        (CertificateTypes.CLIENT_CERT, "Client Certificate"),
        (CertificateTypes.CODE_SIGNING_CERT, "Code Signing Certificate"),
        (CertificateTypes.OCSP, "OCSP Signing Certificate"),
    )
    type = models.CharField(max_length=1, choices=TYPES)
    name = models.CharField(
        max_length=128,
        validators=[alphanumeric],
        blank=True,
        help_text="Name of your key, if not set will be equal to your CommonName.",
    )

    dn = models.ForeignKey(DistinguishedName, on_delete=models.PROTECT)

    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        help_text="The signing authority (None for root certificate)",
        on_delete=models.PROTECT,
    )

    crl_distribution_url = models.URLField(
        "CRL distribution url",
        validators=[crl_url_validator],
        blank=True,
        null=True,
        help_text="Base URL for certificate revocation list (CRL)",
    )
    ocsp_distribution_host = models.URLField(
        "OCSP distribution host",
        blank=True,
        null=True,
        help_text="Host URL for Online Certificate Status Protocol (OCSP)",
    )

    created_at = models.DateField(auto_now_add=True)
    expires_at = models.DateField(
        validators=[validate_in_future],
        help_text="Select the date that the certificate will expire: for root typically 20 years, "
        "for intermediate 10 years for other types 1 year.",
    )
    revoked_at = models.DateTimeField(editable=False, default=None, blank=True, null=True)
    # when not revoked, uuid is 0. The revoked_uuid is used in the unique constraint
    # to ensure only one signed certificate has been issued
    revoked_uuid = models.UUIDField(default=0)
    serial = models.UUIDField(default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    passphrase_issuer = ""
    passphrase_out = ""
    passphrase_out_confirmation = ""

    @property
    def days_valid(self):
        if self.created_at:
            return int((self.expires_at - self.created_at).days)
        else:
            return int((self.expires_at - timezone.now().date()).days)

    @property
    def slug_revoked_at(self):
        if self.revoked_at:
            return slugify(self.revoked_at)

    @property
    def slug_name(self):
        return slugify(self.name)

    @property
    def revoked(self):
        return self.revoked_uuid != uuid.UUID(int=0)

    @property
    def expired(self):
        return self.expires_at <= timezone.now().date()

    def is_passphrase_valid(self, passphrase):
        if not hasattr(self, "keystore"):
            raise KeyStore.DoesNotExist("Certificate has no cert, " "something went wrong during generation")
        valid = check_passphrase_issuer(self.keystore.key, passphrase)
        return bool(valid)

    def get_certificate_info(self):
        if not hasattr(self, "keystore"):
            raise KeyStore.DoesNotExist("Certificate has no cert, " "something went wrong during generation")
        crt = self.keystore.crt
        info = get_certificate_info(crt)
        return info

    # Create only model
    def save(self, *args, **kwargs):
        if self.id is None:
            self.full_clean()
            super().save(*args, **kwargs)

    def renew(self, expires_at, *args, **kwargs):
        if self.id is None:
            raise ValidationError("Can only renew a saved certificate")
        if self.revoked_at:
            raise ValidationError("Cannot renew a revoked certificate")

        if self.type not in [
            CertificateTypes.SERVER_CERT,
            CertificateTypes.CLIENT_CERT,
            CertificateTypes.CODE_SIGNING_CERT,
            CertificateTypes.OCSP,
        ]:
            raise ValidationError("Can not renew intermediate " "or root certificates")
        validate_in_future(expires_at)

        original_name = self.name

        self.delete()

        self.name = original_name
        self.pk = None
        self.revoked_at = None
        self.revoked_uuid = 0
        self.serial = uuid.uuid4()  # Generate new serial number for renewed certificate
        # https://blog.nirmites.com/how-to-duplicate-model-instances-in-django-and-populate-the-database-quickly/
        # might break in the future
        self._state.adding = True
        self.expires_at = expires_at
        self.save()
        return self

    def renew_revocation_list(self, *args, **kwargs):
        if self.id is None:
            raise ValidationError("Can only renew a saved certificate revocation list")
        if self.revoked_at:
            raise ValidationError("Cannot renew a crl of revoked certificate")

        if self.type not in [CertificateTypes.ROOT, CertificateTypes.INTERMEDIATE]:
            raise ValidationError("Can only renew crl of Root or Intermediate certificate")

        revoked_certs = Certificate.objects.filter(parent=self, revoked_at__isnull=False)
        crl_list = [(rc.keystore.crt, rc.revoked_at) for rc in revoked_certs if hasattr(rc, "keystore")]
        last_update = self.crlstore.last_update if hasattr(self, "crlstore") else timezone.now()
        next_update_days = datetime.timedelta(settings.CRL_UPDATE_DAYS_FUTURE, 0, 0)
        next_update = datetime.datetime.now(tz=pytz.UTC) + next_update_days
        crl = revocation_list_builder(crl_list, self, self.passphrase_in, last_update, next_update)

        if not self.crlstore:
            crlstore = CrlStore(certificate=self)
            crlstore.crl = serialize(crl)
            crlstore.save()
        else:
            self.crlstore.crl = serialize(crl)
            self.crlstore.save()

    def force_delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.revoked_at:
            return

        self.revoked_at = timezone.now()
        self.revoked_uuid = uuid.uuid4()
        self.name = f"{self.name}_revoked-{self.revoked_at.isoformat()}"
        kwargs["update_fields"] = ["revoked_at", "revoked_uuid", "name"]
        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        if "passphrase_issuer" in kwargs:
            self.passphrase_issuer = kwargs.pop("passphrase_issuer")
        if "passphrase_out" in kwargs:
            self.passphrase_out = kwargs.pop("passphrase_out")
        if "passphrase_out_confirmation" in kwargs:
            self.passphrase_out_confirmation = kwargs.pop("passphrase_out_confirmation")
        super().__init__(*args, **kwargs)

    class Meta:
        unique_together = [
            ["name", "owner", "type", "revoked_uuid"],
            ["dn", "type", "revoked_uuid"],
        ]

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)


@receiver(pre_save, sender=Certificate)
def set_fields_certificate(sender, instance, *args, **kwargs):
    if not instance.name:
        instance.name = str(instance.dn.commonName)


def check_if_not_update_certificate(instance, *args, **kwargs):
    if instance.id:  # check_if_not_update_certificate
        if (
            kwargs
            and "update_fields" in kwargs
            and set(kwargs["update_fields"]) == set(["revoked_at", "revoked_uuid", "name"])
            and (
                instance.type in {CertificateTypes.SERVER_CERT, CertificateTypes.CLIENT_CERT},
                CertificateTypes.ROOT,
                CertificateTypes.INTERMEDIATE,
            )
        ):
            return
        raise ValidationError("Not allowed to update a Certificate record")


def check_if_passphrases_are_matching(instance, *args, **kwargs):
    if (
        instance.passphrase_out
        and instance.passphrase_out_confirmation
        and instance.passphrase_out != instance.passphrase_out_confirmation
    ):
        raise ValidationError("The two passphrase fields didn't match.")


def check_if_root_has_no_parent(instance, *args, **kwargs):
    if instance.type == CertificateTypes.ROOT and instance.parent:
        raise ValidationError("Not allowed to have a parent certificate for a Root CA certificate")


def check_if_only_root_intermediate_has_crl_or_ocsp(instance, *args, **kwargs):
    if instance.type not in [CertificateTypes.ROOT, CertificateTypes.INTERMEDIATE]:
        if instance.crl_distribution_url:
            raise ValidationError("CRL distribution url only allowed for root and intermediate certificates")
        if instance.ocsp_distribution_host:
            raise ValidationError("OCSP distribution host only allowed for root and intermediate certificates")


def check_if_non_root_certificate_has_parent(instance, *args, **kwargs):
    if instance.type is not CertificateTypes.ROOT:
        if not instance.parent:
            raise ValidationError("Non Root certificate should have a parent")
        cert_types = {
            CertificateTypes.CLIENT_CERT: "Client",
            CertificateTypes.SERVER_CERT: "Server",
            CertificateTypes.CODE_SIGNING_CERT: "Codesigning",
            CertificateTypes.OCSP: "OCSP",
        }
        if instance.parent.type is not CertificateTypes.INTERMEDIATE and instance.type in cert_types:
            raise ValidationError(
                "{} certificate can only be generated for " "intermediate CA parent".format(cert_types[instance.type])
            )


def check_intermediate_policies(instance, *args, **kwargs):
    if instance.type is CertificateTypes.INTERMEDIATE and instance.parent.type is CertificateTypes.ROOT:
        if instance.dn.countryName != instance.parent.dn.countryName:
            raise ValidationError("Country name of Intermediate CA and Root CA should match (policy strict)")
        if instance.dn.stateOrProvinceName != instance.parent.dn.stateOrProvinceName:
            raise ValidationError("State Or Province Name of Intermediate CA and Root CA should match (policy strict)")
        if instance.dn.organizationName != instance.parent.dn.organizationName:
            raise ValidationError("Organization Name of Intermediate CA and Root CA should match (policy strict)")


def check_if_child_not_expires_after_parent(instance, *args, **kwargs):
    if instance.parent and instance.days_valid > instance.parent.days_valid:
        raise ValidationError(
            "Child Certificate (expire date: {}) should not "
            "expire later than parent CA (expire date: {})".format(instance.expires_at, instance.parent.expires_at)
        )


@receiver(pre_save, sender=Certificate)
def validation_rules_certificate(sender, instance, *args, **kwargs):
    check_if_not_update_certificate(instance, *args, **kwargs)
    check_if_root_has_no_parent(instance, *args, **kwargs)
    check_if_only_root_intermediate_has_crl_or_ocsp(instance, *args, **kwargs)
    check_if_non_root_certificate_has_parent(instance, *args, **kwargs)
    check_intermediate_policies(instance, *args, **kwargs)
    check_if_child_not_expires_after_parent(instance, *args, **kwargs)
    check_if_passphrases_are_matching(instance, *args, **kwargs)


class KeyStore(models.Model):
    key = models.TextField("Serialized Private Key")
    crt = models.TextField("Serialized signed certificate")
    p12 = models.BinaryField("Serialized PKCS 12 package with key and certificate", null=True, blank=True, default=None)
    p12_legacy = models.BinaryField(
        "Serialized PKCS 12 package with key and certificate sha1 for legacy support",
        null=True,
        blank=True,
        default=None,
    )

    fingerprint = models.TextField("SHA1 Fingerprint of Certificate")
    certificate = models.OneToOneField(
        Certificate,
        on_delete=models.CASCADE,
    )

    def _get_fingerprint(self):
        if not self.crt:
            raise KeyStore.DoesNotExist("Certificate has no cert, " "something went wrong during generation")
        info = get_certificate_fingerprint(self.crt)
        return info

    # Create only model
    def save(self, full_clean=True, *args, **kwargs):
        if self.id is None:
            if full_clean:
                self.fingerprint = self._get_fingerprint()
                self.full_clean()
            super().save(*args, **kwargs)
        else:
            raise RuntimeError("Not allowed to update a KeyStore record")


class CrlStore(models.Model):
    crl = models.TextField("Serialized CRL certificate", blank=True, null=True)
    last_update = models.DateTimeField(
        auto_now=True, editable=False, help_text="Date at which last crl has been generated"
    )

    certificate = models.OneToOneField(
        Certificate,
        on_delete=models.CASCADE,
    )


def check_passphrase_issuer(key, passphrase):
    from certificate_engine.ssl.key import Key as KeyObjGenerator

    return KeyObjGenerator().check_passphrase(key, passphrase)


@receiver(pre_save, sender=Certificate)
def check_policies_certificate(sender, instance, **kwargs):
    from certificate_engine.ssl.certificate import Certificate as CertificateObjGenerator

    if instance.revoked:
        # Don't check policies in case of revocation
        return

    certhandler = CertificateObjGenerator()
    certhandler.check_policies(instance)


@receiver(post_save, sender=Certificate)
def generate_certificate(sender, instance, created, **kwargs):
    if created:
        keystore = KeyStore(certificate=instance)
        key_size = None
        if settings.KEY_ALGORITHM == "rsa":
            key_size = 4096 if instance.type in [CertificateTypes.ROOT, CertificateTypes.INTERMEDIATE] else 2048
        key = KeyGenerator().create_key(settings.KEY_ALGORITHM, key_size)
        keystore.key = key.serialize(instance.passphrase_out)
        certhandler = CertificateGenerator()
        certhandler.create_certificate(instance, keystore.key, instance.passphrase_out, instance.passphrase_issuer)
        keystore.crt = certhandler.serialize()
        if instance.type not in [CertificateTypes.ROOT, CertificateTypes.INTERMEDIATE]:
            root_certificate = CertificateGenerator().load(instance.parent.parent.keystore.crt).certificate
            int_certificate = CertificateGenerator().load(instance.parent.keystore.crt).certificate
            keystore.p12 = key.serialize_pkcs12(
                instance.name,
                certhandler.certificate,
                instance.passphrase_out,
                cas=[int_certificate, root_certificate],
                encryption_legacy=False,
            )

            keystore.p12_legacy = key.serialize_pkcs12(
                instance.name,
                certhandler.certificate,
                instance.passphrase_out,
                cas=[int_certificate, root_certificate],
                encryption_legacy=True,
            )
        keystore.save()

        if instance.type in [CertificateTypes.ROOT, CertificateTypes.INTERMEDIATE]:
            next_update_days = datetime.timedelta(settings.CRL_UPDATE_DAYS_FUTURE, 0, 0)
            next_update = datetime.datetime.now(tz=pytz.UTC) + next_update_days
            crl = revocation_list_builder([], instance, instance.passphrase_out, next_update=next_update)
            crlstore = CrlStore(certificate=instance)
            crlstore.crl = serialize(crl)
            crlstore.save()


@receiver(post_save, sender=Certificate)
def update_certificate_revocation_list(sender, instance, created, **kwargs):
    update_fields = kwargs["update_fields"]
    if not created and "revoked_uuid" in update_fields:
        if instance.type == CertificateTypes.ROOT:
            return

        if not instance.parent:
            RuntimeError(f"Cannot build revoke list of certificate {instance} without parent")

        revoked_certs = Certificate.objects.filter(parent=instance.parent, revoked_at__isnull=False)
        crl_list = [(rc.keystore.crt, rc.revoked_at) for rc in revoked_certs if hasattr(rc, "keystore")]
        last_update = instance.parent.crlstore.last_update if hasattr(instance.parent, "crlstore") else timezone.now()

        next_update_days = datetime.timedelta(settings.CRL_UPDATE_DAYS_FUTURE, 0, 0)
        next_update = datetime.datetime.now(tz=pytz.UTC) + next_update_days
        crl = revocation_list_builder(crl_list, instance.parent, instance.passphrase_issuer, last_update, next_update)
        if not hasattr(instance.parent, "crlstore"):
            crlstore = CrlStore(certificate=instance.parent)
            crlstore.crl = serialize(crl)
            crlstore.save()
        else:
            instance.parent.crlstore.crl = serialize(crl)
            instance.parent.crlstore.save()
