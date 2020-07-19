"""Models for storing subject and certificate information"""

import uuid
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone
from django_countries.fields import CountryField

from certificate_engine.generator import (
    generate_crl_file, get_certificate_info, is_passphrase_in_valid, revoke_client_cert, revoke_server_cert)
from certificate_engine.types import CertificateTypes


class DistinguishedName(models.Model):
    alphanumeric_validator = RegexValidator(
        r'^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ \*]*$',
        'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')
    country_validator = RegexValidator(
        r'^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ \*]*$',
        'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')

    countryName = CountryField(
        "Country Name",
        help_text="The two-character country name in ISO 3166 format.",
        blank=True,
        null=True)
    stateOrProvinceName = models.CharField(
        "State or Province Name",
        max_length=128,
        validators=[alphanumeric_validator],
        help_text="The state/region where your organization is located. " +
        "This shouldn't be abbreviated. (1–128 characters)",
        blank=True,
        null=True)
    localityName = models.CharField(
        "Locality Name",
        max_length=128,
        validators=[alphanumeric_validator],
        help_text="The city where your organization is located. (1–128 characters)",
        blank=True,
        null=True)
    organizationName = models.CharField(
        "Organization Name",
        max_length=64,
        validators=[alphanumeric_validator],
        help_text="The legal name of your organization. This should not be abbreviated and should include " +
        "suffixes such as Inc, Corp, or LLC.",
        blank=True,
        null=True)
    organizationalUnitName = models.CharField(
        "Organization Unit Name",
        max_length=64,
        validators=[alphanumeric_validator],
        help_text="The division of your organization handling the certificate.",
        blank=True,
        null=True)
    emailAddress = models.EmailField(
        "Email Address",
        max_length=64,
        validators=[alphanumeric_validator],
        default="ca@repleo.nl",
        help_text="The email address to contact your organization. Also used by BounCA for authentication.",
        blank=True,
        null=True)
    commonName = models.CharField(
        "Common Name",
        max_length=64,
        validators=[alphanumeric_validator],
        help_text="The fully qualified domain name (FQDN) of your server. This must match " +
        "exactly what you type in your web browser or you will receive a name mismatch error.")
    subjectAltNames = ArrayField(
        models.CharField(
            max_length=64,
            validators=[alphanumeric_validator]),
        help_text="subjectAltName list, i.e. dns names for server certs and email adresses " +
        "for client certs. (separate by comma)",
        blank=True,
        null=True)

    def _to_dn(self, email_label='EMAIL'):
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
            dn.append("{}}={}".format(self.email_label, self.emailAddress))
        if self.countryName is not None:
            dn.append("C={}".format(self.countryName))
        return dn

    @property
    def dn(self):
        return self._to_dn(email_label='EMAIL').join(', ')

    @property
    def subj(self):
        return ([''] + self._to_dn(email_label='emailAddress')).join('/')

    # Create only model
    def save(self, *args, **kwargs):
        if self.id is None:
            super(DistinguishedName, self).save(*args, **kwargs)

    @property
    def slug_commonName(self):
        return slugify(self.commonName)

    def __unicode__(self):
        return str(self.commonName)

    def __str__(self):
        return str(self.commonName)


@receiver(pre_save, sender=DistinguishedName)
def validation_rules_distinguished_name(sender, instance, *args, **kwargs):
    if instance.id:
        raise ValidationError(
            'Not allowed to update a DistinguishedName record')


def validate_in_future(value):
    if value <= timezone.now().date():
        raise ValidationError('%s is not in the future!' % value)


class CertificateQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete()


class Certificate(models.Model):
    objects = CertificateQuerySet.as_manager()
    alphanumeric = RegexValidator(
        r'^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ ]*$',
        'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')
    alphanumericshort = RegexValidator(
        r'^[0-9a-zA-Z\_\.]*$',
        'Only alphanumeric characters and [_.] are allowed.')

    TYPES = (
        (CertificateTypes.ROOT, 'Root CA Certificate'),
        (CertificateTypes.INTERMEDIATE, 'Intermediate CA Certificate'),
        (CertificateTypes.SERVER_CERT, 'Server Certificate'),
        (CertificateTypes.CLIENT_CERT, 'Client Certificate'),
        (CertificateTypes.OCSP, 'OCSP Signing Certificate'),
    )
    type = models.CharField(max_length=1, choices=TYPES)
    shortname = models.CharField(
        "Short Name",
        max_length=128,
        validators=[alphanumericshort],
        help_text="Short name to identify your key.")
    name = models.CharField(
        max_length=128,
        validators=[alphanumeric],
        blank=True,
        help_text="Long name of your key, if not set will be equal to your shortname + CommonName.")

    dn = models.ForeignKey(DistinguishedName, on_delete=models.PROTECT)

    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        help_text="The signing authority (None for root certificate)",
        on_delete=models.PROTECT)

    crl_distribution_url = models.URLField(
        "CRL distribution url",
        blank=True,
        null=True,
        help_text="Base URL for certificate revocation list (CRL)")
    ocsp_distribution_host = models.URLField(
        "OCSP distribution host",
        blank=True,
        null=True,
        help_text="Host URL for Online Certificate Status Protocol (OCSP)")

    created_at = models.DateField(auto_now_add=True)
    expires_at = models.DateField(
        validators=[validate_in_future],
        help_text="Select the date that the certificate will expire: for root typically 20 years, " +
        "for intermediate 10 years for other types 1 year. Allowed date format: yyyy-mm-dd.")
    revoked_at = models.DateField(
        editable=False, default=None, blank=True, null=True)
    revoked_uuid = models.UUIDField(default=0)  # TODO check this
    serial = models.UUIDField(default=uuid.uuid4, editable=False)

    key = models.TextField("Serialized Private Key")
    crt = models.TextField("Serialized signed certificate")

    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    passphrase_in = ""
    passphrase_out = ""
    passphrase_out_confirmation = ""

    @property
    def days_valid(self):
        if self.created_at:
            return int((self.expires_at - self.created_at).days)
        else:
            return int((self.expires_at - timezone.now().date()).days)

    # TODO days_valid.fget.short_description = 'Days valid'

    @property
    def slug_revoked_at(self):
        return slugify(self.revoked_at)

    @property
    def revoked(self):
        return (self.revoked_uuid != uuid.UUID(
            '00000000000000000000000000000001'))

    @property
    def expired(self):
        return self.expires_at <= timezone.now().date()

    @property
    def cert_path(self):
        if self.parent:
            cert_path = self.parent.cert_path
            cert_path.append({'id': self.id, 'shortname': self.shortname})
            return cert_path
        else:
            return [{'id': self.id, 'shortname': self.shortname}]

    def is_passphrase_valid(self):
        valid = is_passphrase_in_valid(self)
        if valid:
            return True
        else:
            return False

    def get_certificate_info(self):
        info = get_certificate_info(self)
        return info

    # Create only model
    def save(self, *args, **kwargs):
        if self.id is None:
            super(Certificate, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.revoked_at and (
                self.type is CertificateTypes.SERVER_CERT or self.type is CertificateTypes.CLIENT_CERT):
            self.revoked_at = timezone.now()
            self.revoked_uuid = uuid.uuid4()
            if self.type == CertificateTypes.SERVER_CERT:
                revoke_server_cert(self)
            if self.type == CertificateTypes.CLIENT_CERT:
                revoke_client_cert(self)
            self.save(*args, **kwargs)
            return None
        raise ValidationError('Delete of record not allowed')

    def generate_crl(self, *args, **kwargs):
        if self.type is CertificateTypes.INTERMEDIATE:
            generate_crl_file(self)
            return
        raise ValidationError(
            'CRL File can only be generated for Intermediate Certificates')

    def __init__(self, *args, **kwargs):
        if 'passphrase_in' in kwargs:
            self.passphrase_in = kwargs.pop('passphrase_in')
        if 'passphrase_out' in kwargs:
            self.passphrase_out = kwargs.pop('passphrase_out')
        if 'passphrase_out_confirmation' in kwargs:
            self.passphrase_out_confirmation = kwargs.pop(
                'passphrase_out_confirmation')
        super().__init__(*args, **kwargs)

    class Meta:
        unique_together = (('shortname', 'type', 'revoked_uuid'),
                           ('dn', 'type', 'revoked_uuid'),)

    def __unicode__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)


@receiver(pre_save, sender=Certificate)
def set_fields_certificate(sender, instance, *args, **kwargs):
    if not instance.name:
        instance.name = str(instance.shortname) + " - " + \
            str(instance.dn.commonName)


@receiver(pre_save, sender=Certificate)
def validation_rules_certificate(sender, instance, *args, **kwargs):
    if instance.id:  # check_if_not_update_certificate
        # allow update of revoked_at field, this is a bit buggy: should filter
        # all other fields TODO
        if instance.revoked_at and (
                instance.type is CertificateTypes.SERVER_CERT or instance.type is CertificateTypes.CLIENT_CERT):
            return
        raise ValidationError('Not allowed to update a Certificate record')

    if instance.passphrase_out and instance.passphrase_out_confirmation and \
       instance.passphrase_out != instance.passphrase_out_confirmation:
        raise ValidationError("The two passphrase fields didn't match.")

    if instance.type == CertificateTypes.ROOT and instance.parent:  # check_if_root_has_no_parent
        raise ValidationError(
            'Not allowed to have a parent certificate for a ROOT CA certificate')
    # check_if_non_root_certificate_has_parent
    if instance.type is not CertificateTypes.ROOT and not instance.parent:
        raise ValidationError('Non ROOT certificate should have a parent')
    # check_if_non_root_certificate_has_parent
    if instance.type is CertificateTypes.SERVER_CERT and instance.parent.type is not CertificateTypes.INTERMEDIATE:
        raise ValidationError(
            'Server certificate can only be generated for intermediate CA parent')
    # check_if_non_root_certificate_has_parent
    if instance.type is CertificateTypes.CLIENT_CERT and instance.parent.type is not CertificateTypes.INTERMEDIATE:
        raise ValidationError(
            'Client certificate can only be generated for intermediate CA parent')

    if instance.type is CertificateTypes.INTERMEDIATE and instance.parent.type is CertificateTypes.ROOT:
        if instance.dn.countryName != instance.parent.dn.countryName:
            raise ValidationError(
                'Country name of Intermediate CA and Root CA should match (policy strict)')
        if instance.dn.stateOrProvinceName != instance.parent.dn.stateOrProvinceName:
            raise ValidationError(
                'State Or Province Name of Intermediate CA and Root CA should match (policy strict)')
        if instance.dn.organizationName != instance.parent.dn.organizationName:
            raise ValidationError(
                'Organization Name of Intermediate CA and Root CA should match (policy strict)')

    if instance.parent and instance.days_valid > instance.parent.days_valid:
        raise ValidationError(
            'Child Certificate should not expire later than ROOT CA')

