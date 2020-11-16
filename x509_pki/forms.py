"""Certificate create forms"""

from django import forms
from django.contrib.auth import password_validation
from django.utils import timezone

from certificate_engine.types import CertificateTypes

from .models import Certificate, DistinguishedName


class DistinguishedNameForm(forms.ModelForm):

    def clean(self):
        """ This is the form's clean method, not a particular field's clean method """

        pk = self.instance.pk
        if pk is not None:
            raise forms.ValidationError(
                'Not allowed to update an existing certificate!')

    class Meta:
        model = DistinguishedName
        fields = (
            'commonName',
            'countryName',
            'stateOrProvinceName',
            'localityName',
            'organizationName',
            'organizationalUnitName',
            'emailAddress',
            'subjectAltNames')


class CertificateForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': "The two passphrase fields didn't match."
    }

    passphrase_issuer = forms.CharField(
        label="Passphrase issuer",
        initial="",
        required=False,
        widget=forms.PasswordInput,
        strip=False,
        help_text="The passphrase for unlocking your signing key.",
    )
    passphrase_out = forms.CharField(
        label="New passphrase",
        initial="",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Passphrase for protecting the key of your new certificate.",
    )
    passphrase_out_confirmation = forms.CharField(
        label="New passphrase confirmation",
        initial="",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Enter the same passphrase as before, for verification.",
    )

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        inst = super().save(commit=False)
        inst.owner = self._user
        if commit:
            inst.save()
        return inst

    def validate(self, data):
        if data['passphrase_out1'] != data['passphrase_out_confirmation']:
            raise forms.ValidationError(
                "The two passphrase fields didn't match.")
        return data

    def clean_passphrase_issuer(self):
        passphrase_issuer = self.cleaned_data.get("passphrase_issuer")
        if passphrase_issuer:
            if not self.cleaned_data.get('parent'):
                raise forms.ValidationError(
                    "You should provide a parent certificate if you provide a passphrase in")
            parent = Certificate.objects.get(
                pk=self.cleaned_data.get('parent'))
            if not parent.is_passphrase_valid():
                raise forms.ValidationError(
                    "Passphrase issuer incorrect. Not allowed to sign your certificate")
            return passphrase_issuer
        return None

    def clean_passphrase_out(self):
        passphrase_out = self.cleaned_data.get("passphrase_out")
        password_validation.validate_password(passphrase_out, self.instance)
        return passphrase_out

    def clean_passphrase_out_confirmation(self):
        passphrase_out = self.cleaned_data.get("passphrase_out")
        passphrase_out_confirmation = self.cleaned_data.get(
            "passphrase_out_confirmation")
        if passphrase_out and passphrase_out_confirmation and passphrase_out != passphrase_out_confirmation:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        password_validation.validate_password(
            passphrase_out_confirmation, self.instance)
        return passphrase_out_confirmation

    def clean(self):
        cleaned_data = self.cleaned_data

        pk = self.instance.pk
        if pk is not None:
            raise forms.ValidationError(
                'Not allowed to update an existing certificate!')

        name = cleaned_data.get("name")
        cert_type = cleaned_data.get("type")
        dn = cleaned_data.get("dn")
        if Certificate.objects.filter(
                name=name,
                type=cert_type,
                revoked_uuid=0).count() > 0:
            raise forms.ValidationError(
                "name ({}) for {} already exists.".format(name, dict(Certificate.TYPES)[cert_type]))

        if Certificate.objects.filter(
                dn=dn,
                type=cert_type,
                revoked_uuid=0).count() > 0:
            raise forms.ValidationError(
                "DN ({}) for {} already exists.".format(dn, dict(Certificate.TYPES)[cert_type]))

        parent = cleaned_data.get("parent")
        if cert_type == CertificateTypes.ROOT and parent:  # check_if_root_has_no_parent
            raise forms.ValidationError(
                'Not allowed to have a parent certificate for a ROOT CA certificate')

        if cert_type is not CertificateTypes.ROOT and not parent:  # check_if_root_has_no_parent
            raise forms.ValidationError(
                'Non ROOT certificate should have a parent certificate')

        if cert_type is CertificateTypes.SERVER_CERT and not (
                parent.type is CertificateTypes.INTERMEDIATE):  # check_if_non_root_certificate_has_parent
            raise forms.ValidationError(
                'Server certificate can only be generated for intermediate CA parent')

        if cert_type is CertificateTypes.CLIENT_CERT and not (
                parent.type is CertificateTypes.INTERMEDIATE):  # check_if_non_root_certificate_has_parent
            raise forms.ValidationError(
                'Client certificate can only be generated for intermediate CA parent')

        if cert_type is CertificateTypes.SERVER_CERT or cert_type is CertificateTypes.CLIENT_CERT:
            if Certificate.objects.filter(
                    dn=dn,
                    parent=parent,
                    type=CertificateTypes.INTERMEDIATE).count() > 0:
                raise forms.ValidationError(
                    "DN ({}) for {}-Certificate already "
                    "used as intermediate CA.".format(dn, dict(Certificate.TYPES)[cert_type]))

        if cert_type is CertificateTypes.INTERMEDIATE and parent.type is CertificateTypes.ROOT:
            if dn.countryName != parent.dn.countryName:
                raise forms.ValidationError(
                    'Country name of Intermediate CA and Root CA should match (policy strict)')
            if dn.stateOrProvinceName != parent.dn.stateOrProvinceName:
                raise forms.ValidationError(
                    'State Or Province Name of Intermediate CA and Root CA should match (policy strict)')
            if dn.organizationName != parent.dn.organizationName:
                raise forms.ValidationError(
                    'Organization Name of Intermediate CA and Root CA should match (policy strict)')

        if cleaned_data.get('expires_at'):
            now = timezone.now().date()
            expires_at = cleaned_data.get("expires_at")

            days_valid = int((expires_at - now).days)
            if parent and days_valid > parent.days_valid:
                raise forms.ValidationError(
                    'Child Certificate expiration data should be before parent expiration date')

        #TODO is this expected behavior? Check with standards
        if cert_type is CertificateTypes.INTERMEDIATE and parent.crl_distribution_url:
            cleaned_data['crl_distribution_url'] = parent.crl_distribution_url

        if cert_type is CertificateTypes.INTERMEDIATE and parent.ocsp_distribution_host:
            cleaned_data['ocsp_distribution_host'] = parent.ocsp_distribution_host

        return cleaned_data

    class Meta:
        model = Certificate
        fields = (
            'name',
            'parent',
            'type',
            'dn',
            'expires_at',
            'crl_distribution_url',
            'ocsp_distribution_host')


class CertificateRevokeForm(forms.ModelForm):
    passphrase_issuer = forms.CharField(
        label="Passphrase in",
        initial="",
        widget=forms.PasswordInput,
        strip=False,
        #        help_text=password_validation.password_validators_help_text_html(),
        help_text="The passphrase for unlocking your signing key.",
    )

    def clean_passphrase_issuer(self, passphrase_issuer):
        if passphrase_issuer:
            if not self.cleaned_data.get('parent'):
                raise forms.ValidationError(
                    "You should provide a parent certificate if you provide a passphrase in")
            parent = Certificate.objects.get(
                pk=self.cleaned_data.get('parent'))
            if not parent.is_passphrase_valid():
                raise forms.ValidationError(
                    "Passphrase issuer incorrect. Not allowed to sign your certificate")
            return passphrase_issuer
        return None

    class Meta:
        model = Certificate
        fields = ()


class CertificateCRLForm(forms.ModelForm):

    passphrase_issuer = forms.CharField(
        label="Passphrase issuer",
        initial="",
        widget=forms.PasswordInput,
        strip=False,
        #        help_text=password_validation.password_validators_help_text_html(),
        help_text="The passphrase for unlocking your signing key.",
    )

    def clean_passphrase_issuer(self, passphrase_issuer):
        if passphrase_issuer:
            if not self.cleaned_data.get('parent'):
                raise forms.ValidationError(
                    "You should provide a parent certificate if you provide a passphrase in")
            parent = Certificate.objects.get(
                pk=self.cleaned_data.get('parent'))
            if not parent.is_passphrase_valid():
                raise forms.ValidationError(
                    "Passphrase issuer incorrect. Not allowed to sign your certificate")
            return passphrase_issuer
        return None

    class Meta:
        model = Certificate
        fields = ()
