from django.db import models
from django_countries.fields import CountryField
from django.core.validators import RegexValidator

class DistinguishedName(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ \*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')

    countryName                 = CountryField(default="NL",help_text="The two-character country name in ISO 3166 format.")
    stateOrProvinceName         = models.CharField(max_length=128,validators=[alphanumeric],editable=False,default="Noord Holland",help_text="The state/region where your organization is located. This shouldn't be abbreviated. The stateorprov is 1–128 characters.")
    localityName                = models.CharField(max_length=128,validators=[alphanumeric],editable=False,default="Amstelveen",help_text="The city where your organization is located. The locality is 1–128 characters.")
    organizationName            = models.CharField(max_length=64,validators=[alphanumeric],editable=False,default="Repleo",help_text="The legal name of your organization. This should not be abbreviated and should include suffixes such as Inc, Corp, or LLC.")
    organizationalUnitName      = models.CharField(max_length=64,validators=[alphanumeric],editable=False,default="IT Department",help_text="The division of your organization handling the certificate.")
    emailAddress                = models.EmailField(max_length=64,validators=[alphanumeric],editable=False,default="ca@repleo.nl",help_text="An email address used to contact your organization.")
    commonName                  = models.CharField(max_length=64,validators=[alphanumeric],editable=False,default="*.repleo.nl",help_text="The fully qualified domain name (FQDN) of your server. This must match exactly what you type in your web browser or you will receive a name mismatch error.")

    @property
    def dn(self):
        return  'CN='+ str(self.commonName) +\
                ', O='+ str(self.organizationName) +\
                ', OU='+ str(self.organizationalUnitName) +\
                ', L='+ str(self.localityName) +\
                ', ST='+ str(self.stateOrProvinceName) +\
                ', EMAIL=' + str(self.emailAddress.code) +\
                ', C=' + str(self.countryName.code)
       
    class Meta:
        db_table = 'bounca_distinguished_name'
        
    def __unicode__(self):
        return  str(self.commonName)

    def __str__(self):
        return  str(self.commonName)
    


class Certificate(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z@#$%^&+=\_\.\-\,\ ]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')
    alphanumericshort = RegexValidator(r'^[0-9a-zA-Z\_\.]*$', 'Only alphanumeric characters and [_.] are allowed.')

    ROOT="R"
    INTERMEDIATE="I"
    SERVER_CERT="S"
    CLIENT_CERT="C"
    OCSP="O"

    TYPE = (
        (ROOT, 'Root Certificate'),
        (INTERMEDIATE,  'Intermediate'),
        (SERVER_CERT,  'Server Certificate'),
        (CLIENT_CERT,  'Client Certificate'),
        (OCSP,  'OCSP Signing Certificate'),

    )
    type                    = models.CharField(max_length=1, choices=TYPE)
    shortname               = models.CharField(max_length=128,editable=False,validators=[alphanumericshort],default="repleo",help_text="Short name used to store your keys and scripts.")
    name                    = models.CharField(max_length=128,validators=[alphanumeric],help_text="Long name of your authority, if not set will be equal to your CommonName.")

    dn                      = models.ForeignKey(DistinguishedName)
    parent                  = models.ForeignKey("self",editable=False,blank=True,null=True)

    class Meta:
        db_table = 'bounca_certificate'
        unique_together = (('shortname', 'type'),)

    def __unicode__(self):
        return  str(self.name)

    def __str__(self):
        return  str(self.name)
