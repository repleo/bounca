from django.db import models
from django_countries.fields import CountryField
from django.core.validators import RegexValidator
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class DistinguishedName(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ \*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')

    countryName                 = CountryField(default="NL",help_text="The two-character country name in ISO 3166 format.")
    stateOrProvinceName         = models.CharField(max_length=128,validators=[alphanumeric],default="Noord Holland",help_text="The state/region where your organization is located. This shouldn't be abbreviated. The stateorprov is 1–128 characters.")
    localityName                = models.CharField(max_length=128,validators=[alphanumeric],default="Amstelveen",help_text="The city where your organization is located. The locality is 1–128 characters.")
    organizationName            = models.CharField(max_length=64,validators=[alphanumeric],default="Repleo",help_text="The legal name of your organization. This should not be abbreviated and should include suffixes such as Inc, Corp, or LLC.")
    organizationalUnitName      = models.CharField(max_length=64,validators=[alphanumeric],default="IT Department",help_text="The division of your organization handling the certificate.")
    emailAddress                = models.EmailField(max_length=64,validators=[alphanumeric],default="ca@repleo.nl",help_text="An email address used to contact your organization.")
    commonName                  = models.CharField(max_length=64,validators=[alphanumeric],default="*.repleo.nl",help_text="The fully qualified domain name (FQDN) of your server. This must match exactly what you type in your web browser or you will receive a name mismatch error.")

    @property
    def dn(self):
        return  'CN='+ str(self.commonName) +\
                ', O='+ str(self.organizationName) +\
                ', OU='+ str(self.organizationalUnitName) +\
                ', L='+ str(self.localityName) +\
                ', ST='+ str(self.stateOrProvinceName) +\
                ', EMAIL=' + str(self.emailAddress) +\
                ', C=' + str(self.countryName)

    @property
    def subj(self):
        return  '/CN='+ str(self.commonName) +\
                '/O='+ str(self.organizationName) +\
                '/OU='+ str(self.organizationalUnitName) +\
                '/L='+ str(self.localityName) +\
                '/ST='+ str(self.stateOrProvinceName) +\
                '/emailAddress=' + str(self.emailAddress) +\
                '/C=' + str(self.countryName)                

    def delete(self):
        raise ValidationError('Delete of record not allowed')
        
    class Meta:
        db_table = 'bounca_distinguished_name'
        
    def __unicode__(self):
        return  str(self.commonName)

    def __str__(self):
        return  str(self.commonName)
    
@receiver(pre_save, sender=DistinguishedName)
def validation_rules_distinguished_name(sender,instance, *args, **kwargs):
    if instance.id:
        raise ValidationError('Not allowed to update a DistinguishedName record')
 
from django.utils import timezone

def validate_in_future(value):
    if value <= timezone.now().date():
        raise ValidationError('%s is not in the future!' % value)
    
class Certificate(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ ]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')
    alphanumericshort = RegexValidator(r'^[0-9a-zA-Z\_\.]*$', 'Only alphanumeric characters and [_.] are allowed.')

    ROOT="R"
    INTERMEDIATE="I"
    SERVER_CERT="S"
    CLIENT_CERT="C"
    OCSP="O"

    TYPES = (
        (ROOT, 'Root Certificate'),
        (INTERMEDIATE,  'Intermediate'),
        (SERVER_CERT,  'Server Certificate'),
        (CLIENT_CERT,  'Client Certificate'),
        (OCSP,  'OCSP Signing Certificate'),

    )
    type                    = models.CharField(max_length=1, choices=TYPES)
    shortname               = models.CharField(max_length=128,validators=[alphanumericshort],help_text="Short name used to store your keys and scripts.")
    name                    = models.CharField(max_length=128,validators=[alphanumeric],blank=True,help_text="Long name of your authority, if not set will be equal to your shortname + CommonName.")

    dn                      = models.ForeignKey(DistinguishedName)
    parent                  = models.ForeignKey("self",blank=True,null=True)

    created_at              = models.DateField(auto_now_add=True)
    expires_at              = models.DateField(validators=[validate_in_future],help_text="Select the date that the certificate will expire: for root typically 20 years, for intermediate 10 years for other types 1 year.")
    
    
    @property
    def days_valid(self):
        return  int((self.expires_at-self.created_at).days)
    days_valid.fget.short_description = 'Days valid'                
    
    def delete(self):
        raise ValidationError('Delete of record not allowed')
    
    class Meta:
        db_table = 'bounca_certificate'
        unique_together = (('shortname', 'type'),)

    def __unicode__(self):
        return  str(self.name)

    def __str__(self):
        return  str(self.name)

@receiver(pre_save, sender=Certificate)
def set_fields_certificate(sender,instance, *args, **kwargs):
    if not instance.name:
        instance.name=str(instance.shortname) + " - " + str(instance.dn.commonName)

@receiver(pre_save, sender=Certificate)
def validation_rules_certificate(sender,instance, *args, **kwargs):
    if instance.id: #check_if_not_update_certificate
        raise ValidationError('Not allowed to update a Certificate record')
    if instance.type == Certificate.ROOT and instance.parent: #check_if_root_has_no_parent
        raise ValidationError('Not allowed to have a parent certificate for a ROOT CA certificate')
    if instance.type is not Certificate.ROOT and not instance.parent: #check_if_non_root_certificate_has_parent
        raise ValidationError('Non ROOT certificate should have a parent')

from ..certificate_engine.generator import generate_root_ca  
@receiver(post_save, sender=Certificate)
def generate_certificate(sender, instance, created, **kwargs):
    if created:
        if instance.type==Certificate.ROOT:
            generate_root_ca(instance,'testtest')
        if instance.type==Certificate.INTERMEDIATE:
            pass
            #generate_root_ca(instance)
            
