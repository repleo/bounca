from pprint import pprint

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Column, Row, Fieldset, ButtonHolder, Field, Div, \
    BaseInput, LayoutObject
from crispy_forms.utils import TEMPLATE_PACK
from django import forms
from django.template.loader import render_to_string
from django.utils.deconstruct import deconstructible

from vuetifyforms.vue import VuetifyFormMixin
from x509_pki.models import DistinguishedName, Certificate


class DistinguishedNameForm(forms.ModelForm):
    class Meta:
        model = DistinguishedName
        fields = [
            'commonName',
            'subjectAltNames',
            'organizationName',
            'organizationalUnitName',
            'emailAddress',
            'countryName',
            'stateOrProvinceName',
            'localityName',
        ]


class AddDistinguishedNameRootCAForm(DistinguishedNameForm):
    scope_prefix = 'cert_data.dn'
    form_name = 'cert_form'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subjectAltNames'].widget = forms.HiddenInput()
        self.fields['commonName'].help_text = \
            'The common name of your certification authority.' + \
            'This field is used to identify your CA in the chain'

@deconstructible
class PasswordConfirmValidator:
    def __init__(self, field):
        self.field = field


class CertificateForm(forms.ModelForm, VuetifyFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dn = DistinguishedNameForm(**kwargs)

    error_messages = {
        'password_mismatch': "The two passphrase fields didn't match."
    }

    passphrase_in = forms.CharField(
        label="Passphrase in",
        initial="",
        widget=forms.PasswordInput,
        strip=False,
        #        help_text=password_validation.password_validators_help_text_html(),
        help_text="The passphrase for unlocking your signing key.",
    )
    passphrase_out = forms.CharField(
        label="Passphrase",
        initial="",
        widget=forms.PasswordInput,
        strip=False,
        #        help_text=password_validation.password_validators_help_text_html(),
        help_text="Passphrase for protecting the key of your new certificate.",
    )
    passphrase_out_confirmation = forms.CharField(
        label="Passphrase confirmation",
        initial="",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Enter the same passphrase as before, for verification.",
        validators=[PasswordConfirmValidator("passphrase_out")]
    )

    class Meta:
        model = Certificate
        fields = [
            'name',
            'parent',
            'dn',
            'type',
            'expires_at',
            'crl_distribution_url',
            'ocsp_distribution_host'
        ]


class Flex(Div):
    """
    Layout object. It wraps fields in a div so the wrapper can be used as a flex. Example::
        Flex('form_field_1', 'form_field_2')
    Flex components will automatically fill the available space in a row or column. They will also shrink relative to the rest of the flex items in the flex container when a specific size is not designated.. Example::
        Flex('form_field_1', xs12=True, md6=True)
    """

    template = "%s/layout/flex.html"


class Spacer(Div):
    """
    Layout object. Spacer for button fields
    """

    template = "%s/layout/spacer.html"


class VueScriptElem(LayoutObject):
    """
    Layout object.

    Abstract class for vue elems
    """

    template = None

    def __init__(self, elems, **kwargs):
        self.elems = elems
        self.template = kwargs.pop("template", self.template)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        template = self.get_template_name(template_pack)
        return render_to_string(template, {"script": self})


class VueImports(VueScriptElem):
    """
    Layout object. Spacer for button fields
    """

    template = "%s/script/imports.js"


class VueMethods(VueScriptElem):
    """
    Layout object. Spacer for button fields
    """

    template = "%s/script/methods.js"


class Submit(BaseInput):
    """
    Used to create a Submit button descriptor for the {% crispy %} template tag::

        submit = Submit('Search the Site', 'search this site')

    .. note:: The first argument is also slugified and turned into the id for the submit button.
    """

    input_type = "submit"

    def __init__(self, *args, **kwargs):
        kwargs.update({'dark': True, 'color': "secondary"})
        self.field_classes = ""
        super().__init__(*args, **kwargs)


class Button(BaseInput):
    """
    Used to create a Submit input descriptor for the {% crispy %} template tag::

        button = Button('Button 1', 'Press Me!')

    .. note:: The first argument is also slugified and turned into the id for the button.
    """

    input_type = "button"

    def __init__(self, *args, **kwargs):
        kwargs.update({'text': True, 'plain': True, 'color': "primary"})
        self.field_classes = ""
        super().__init__(*args, **kwargs)


class VueField(Field):
    """
    Layout object, It contains one field name, and you can add attributes to it easily.
    For setting class attributes, you need to use `css_class`, as `class` is a Python keyword.

    Example::

        Field('field_name', style="color: #333;", css_class="whatever", id="field_name")
    """

    template = "%s/field.html"

    def __init__(self, *args, **kwargs):
        self.fields = list(args)

        if not hasattr(self, "attrs"):
            self.attrs = {}
        else:
            # Make sure shared state is not edited.
            self.attrs = self.attrs.copy()

        if "css_class" in kwargs:
            if "class" in self.attrs:
                self.attrs["class"] += " %s" % kwargs.pop("css_class")
            else:
                self.attrs["class"] = kwargs.pop("css_class")

        self.wrapper_class = kwargs.pop("wrapper_class", None)
        self.template = kwargs.pop("template", self.template)

        # We use kwargs as HTML attributes, turning data_id='test' into data-id='test'
        self.attrs.update({k.replace("_", "-"): v for k, v in kwargs.items()})


class AddRootCAForm(CertificateForm):
    scope_prefix = 'cert_data'
    form_title = 'Root Certificate'
    form_component_name = 'RootCert'
    form_object = 'rootcert'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dn_fields = {f"dn.{f}": DistinguishedNameForm().fields[f]
                     for f in DistinguishedNameForm().fields}
        self.fields.update(dn_fields)
        self.fields.pop('dn')
        self.fields.pop('parent')
        self.fields.pop('type')
        self.fields.pop('passphrase_in')
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset('Distinguished Name',
                             Row(
                                Column('dn.commonName', md="8"),
                                Column('expires_at')
                             ),
                             Row(Column(VueField('dn.subjectAltNames',
                                              multiple=True, chips=True,
                                              deletable_chips=True, append_icon=""),
                                        xs12=True, md12=True)),
                             Row(
                                 Column('dn.organizationName'),
                                 Column('dn.organizationalUnitName', xs12=True, md6=True)
                             ),
                             Row(Column('dn.emailAddress', xs12=True, md12=True)),
                             Row(
                                 Column('dn.stateOrProvinceName', md="5"),
                                 Column('dn.localityName', md="5"),
                                 Column('dn.countryName')
                             ),
                             outlined=True,
                             )
                )
            ),
            Row(
                Column(
                    Fieldset('Revocation Services',
                             'crl_distribution_url',
                             'ocsp_distribution_host',
                             outlined=True,
                             )
                )
            ),
            Row(
                Column(
                    Fieldset('Certificate',
                             'name',
                             Row(
                                 Column('passphrase_out'),
                                 Column('passphrase_out_confirmation')
                             ),
                             outlined=True,
                             )
                )
            ),
            ButtonHolder(
                Spacer(),
                Button('cancel', 'Cancel',  **{'@click': 'onCancel'}),
                Submit('submit', 'Create', **{'@click': 'onCcreateCertificate', 'css_class': 'px-6'}),
                css_class="mt-4",
                outlined=True,
            )
        )
        self.vue_imports = [
                ('certificates', '../../api/certificates')
            ]
        self.vue_methods = [
                """
onCcreateCertificate() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.passphrase_out_visible = false;
      this.passphrase_out_confirmation_visible = false;
      this.rootcert.type = 'R';
      certificates.create(this.rootcert).then((response) => {
          this.$emit('update-dasboard');
          this.resetForm();
          this.$emit('close-dialog');
      }).catch((r) => {
        this.$refs.form.setErrors(r.response.data);
      });
    }
  });
}               """,
                """
onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
}
                """
        ]


      #   """
      # dark
      # color="secondary"
      # class="px-4"
      # @click="register"
      #           """

    # def clean_parent(self):
    #     return None
    #
    #
    # def __init__(self, *args, **kwargs):
    #     kwargs.update(auto_id=False, scope_prefix=self.scope_prefix)
    #     super().__init__(*args, **kwargs)
    #     self.fields.pop('dn')
    #     self.initial['parent'] = None
    #     self.initial['type'] = CertificateTypes.ROOT
    #     self.initial['expires_at'] = timezone.now(
    #     ) + timezone.timedelta(weeks=1040)
    #
    #     self.fields['expires_at'].help_text = \
    #         'Expiration date of the root certificate, ' + \
    #         'typically 20 years. (format: yyyy-mm-dd)'
    #
    #     self.fields['parent'].widget = forms.HiddenInput()
    #     self.fields['type'].widget = forms.HiddenInput()
    #     self.fields['passphrase_issuer'].widget = forms.HiddenInput()
    #     if 'scope_prefix' in kwargs:
    #         kwargs.pop('scope_prefix')
    #     if 'prefix' in kwargs:
    #         kwargs.pop('prefix')
    #     if 'initial' in kwargs and 'dn' in kwargs['initial']:
    #         initial = kwargs.pop('initial')
    #         kwargs['initial'] = initial['dn']
    #     self.dn = AddDistinguishedNameRootCAForm(
    #         scope_prefix='cert_data.dn', **kwargs)


