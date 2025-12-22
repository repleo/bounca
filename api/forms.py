from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, BaseInput, ButtonHolder, Column, Fieldset, Layout, Row
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, UserChangeForm
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from api.models import AuthorisedApp
from vuetifyforms.components import VueField, VueSpacer
from vuetifyforms.vue import VuetifyFormMixin
from x509_pki.models import Certificate, DistinguishedName

User = get_user_model()

# TODO BJA annotation that these forms are not meant for runtime use, only for generating VueForms


class Submit(BaseInput):
    """
    Used to create a Submit button descriptor for the {% crispy %} template tag::

        submit = Submit('Search the Site', 'search this site')

    .. note:: The first argument is also slugified and turned into the id for the submit button.
    """

    input_type = "submit"

    def __init__(self, *args, **kwargs):
        kwargs.update({"dark": True, "color": "secondary"})
        self.field_classes = ""
        super().__init__(*args, **kwargs)


class DangerButton(BaseInput):
    """
    Used to create a Submit button descriptor for the {% crispy %} template tag::

        submit = Submit('Search the Site', 'search this site')

    .. note:: The first argument is also slugified and turned into the id for the submit button.
    """

    input_type = "submit"

    def __init__(self, *args, **kwargs):
        kwargs.update({"dark": True, "color": "red"})
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
        kwargs.update({"text": True, "plain": True, "color": "primary"})
        self.field_classes = ""
        super().__init__(*args, **kwargs)


class TokenForm(forms.ModelForm):
    class Meta:
        model = AuthorisedApp
        fields = [
            "name",
        ]


class DeleteAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "password",
        ]


class DistinguishedNameForm(forms.ModelForm):
    class Meta:
        model = DistinguishedName
        fields = [
            "commonName",
            "subjectAltNames",
            "organizationName",
            "organizationalUnitName",
            "emailAddress",
            "countryName",
            "stateOrProvinceName",
            "localityName",
        ]


@deconstructible
class PasswordConfirmValidator:
    def __init__(self, field):
        self.field = field


class CertificateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dn = DistinguishedNameForm(**kwargs)

    error_messages = {"password_mismatch": "The two passphrase fields didn't match."}

    passphrase_issuer = forms.CharField(
        label="Passphrase issuer",
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
        validators=[PasswordConfirmValidator("passphrase_out")],
    )

    class Meta:
        model = Certificate
        fields = ["name", "parent", "dn", "type", "expires_at", "crl_distribution_url", "ocsp_distribution_host"]


class RenewCertificateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    error_messages = {"password_mismatch": "The two passphrase fields didn't match."}

    passphrase_issuer = forms.CharField(
        label="Passphrase issuer",
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
        validators=[PasswordConfirmValidator("passphrase_out")],
    )

    class Meta:
        model = Certificate
        fields = [
            "expires_at",
        ]


class AddRootCAForm(CertificateForm, VuetifyFormMixin):
    scope_prefix = "cert_data"
    vue_file = "front/src/components/forms/RootCert.vue"
    form_title = "Root Certificate"
    form_component_name = "RootCert"
    form_object = "rootcert"
    vue_card_classes = "elevation-10"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dn_fields = {f"dn.{f}": DistinguishedNameForm().fields[f] for f in DistinguishedNameForm().fields}
        self.fields.update(dn_fields)
        self.fields.pop("dn")
        self.fields.pop("parent")
        self.fields.pop("type")
        self.fields.pop("passphrase_issuer")
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        "Distinguished Name",
                        Row(Column("dn.commonName", md="8"), Column("expires_at")),
                        Row(Column("dn.organizationName"), Column("dn.organizationalUnitName", xs12=True, md6=True)),
                        Row(Column("dn.emailAddress", xs12=True, md12=True)),
                        Row(
                            Column("dn.stateOrProvinceName", md="5"),
                            Column("dn.localityName", md="5"),
                            Column("dn.countryName"),
                        ),
                        outlined=True,
                    )
                )
            ),
            Row(
                Column(
                    Fieldset(
                        "Revocation Services",
                        HTML("<h5>These services are set in the extensions of the issued certificates</h5>"),
                        HTML("<h5>Note: Provide only available services</h5>"),
                        "crl_distribution_url",
                        "ocsp_distribution_host",
                        outlined=True,
                    )
                )
            ),
            Row(
                Column(
                    Fieldset(
                        "Certificate",
                        "name",
                        Row(Column("passphrase_out"), Column("passphrase_out_confirmation")),
                        outlined=True,
                    )
                )
            ),
            ButtonHolder(
                VueSpacer(),
                Button("cancel", "Cancel", **{"@click": "onCancel"}),
                Submit("submit", "Create", **{"@click": "onCreateCertificate", "css_class": "px-6"}),
                css_class="mt-4",
                # TODO BJA outlined=True,
            ),
        )
        self.vue_imports = [("certificates", "../../api/certificates")]
        self.vue_extra_initial_statements = """
const date = new Date();
date.setFullYear(date.getFullYear() + 20);
data['rootcert']['expires_at'] = date.toISOString().slice(0,10);
        """
        self.vue_methods = [
            """
onCreateCertificate() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.passphrase_out_visible = false;
      this.passphrase_out_confirmation_visible = false;
      this.rootcert.type = 'R';
      certificates.create(this.rootcert).then( response  => {
          this.$emit('update-dasboard');
          this.resetForm();
          this.$emit('close-dialog');
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
        this.$refs.form.$el.scrollIntoView({behavior: 'smooth'});
      });
    }
  });
}
            """,
            """
onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
}
            """,
        ]


class AddIntermediateCAForm(CertificateForm, VuetifyFormMixin):
    scope_prefix = "cert_data"
    vue_file = "front/src/components/forms/IntermediateCert.vue"
    form_title = "Intermediate Certificate"
    form_component_name = "IntermediateCert"
    form_object = "intermediatecert"
    vue_card_classes = "elevation-10"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dn_fields = {f"dn.{f}": DistinguishedNameForm().fields[f] for f in DistinguishedNameForm().fields}
        self.fields.update(dn_fields)
        self.fields.pop("dn")
        self.fields.pop("parent")
        self.fields.pop("type")
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        "Distinguished Name",
                        Row(Column("dn.commonName", md="8"), Column("expires_at")),
                        Row(
                            Column(VueField("dn.organizationName", disabled=True)),
                            Column("dn.organizationalUnitName", xs12=True, md6=True),
                        ),
                        Row(Column("dn.emailAddress", xs12=True, md12=True)),
                        Row(
                            Column(VueField("dn.stateOrProvinceName", disabled=True), md="5"),
                            Column("dn.localityName", md="5"),
                            Column(VueField("dn.countryName", disabled=True)),
                        ),
                        outlined=True,
                    )
                )
            ),
            Row(
                Column(
                    Fieldset(
                        "Revocation Services",
                        HTML("<h5>These services are set in the extensions of the issued certificates</h5>"),
                        HTML("<h5>Note: Provide only available services</h5>"),
                        "crl_distribution_url",
                        "ocsp_distribution_host",
                        outlined=True,
                    )
                )
            ),
            Row(
                Column(
                    Fieldset(
                        "Certificate",
                        "name",
                        Row(Column("passphrase_out"), Column("passphrase_out_confirmation")),
                        outlined=True,
                    )
                )
            ),
            Row(
                Column(
                    Fieldset(
                        "Signing credentials",
                        "passphrase_issuer",
                        outlined=True,
                    )
                )
            ),
            ButtonHolder(
                VueSpacer(),
                Button("cancel", "Cancel", **{"@click": "onCancel"}),
                Submit("submit", "Create", **{"@click": "onCreateCertificate", "css_class": "px-6"}),
                css_class="mt-4",
                # TODO BJA outlined=True,
            ),
        )
        self.vue_imports = [("certificates", "../../api/certificates")]
        self.vue_props = ["parent"]
        self.vue_extra_initial_statements = """
const date = new Date();
date.setFullYear(date.getFullYear() + 10);
data['intermediatecert']['expires_at'] = date.toISOString().slice(0,10);
        """
        self.vue_extra_init_rules = """
this.setParentData();
            """
        self.vue_watchers = []
        self.vue_mounted = """
this.setParentData();
            """
        self.vue_methods = [
            """
setParentData() {
    this.intermediatecert.dn.organizationName = this.parent.dn.organizationName;
    this.intermediatecert.dn.stateOrProvinceName = this.parent.dn.stateOrProvinceName;
    this.intermediatecert.dn.countryName = this.parent.dn.countryName;
    this.intermediatecert.dn.localityName = this.parent.dn.localityName;
    this.intermediatecert.dn.organizationalUnitName = this.parent.dn.organizationalUnitName;
    this.intermediatecert.dn.emailAddress = this.parent.dn.emailAddress;
}
            """,
            """
onCreateCertificate() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.passphrase_out_visible = false;
      this.passphrase_out_confirmation_visible = false;
      this.passphrase_in_visible = false;
      this.intermediatecert.type = 'I';
      this.intermediatecert.parent = this.parent.id;
      certificates.create(this.intermediatecert).then( response  => {
          this.$emit('update-dasboard');
          this.resetForm();
          this.$emit('close-dialog');
          this.setParentData();
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
        this.$refs.form.$el.scrollIntoView({behavior: 'smooth'});
      });
    }
  });
}
            """,
            """
onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
  this.setParentData();
}
            """,
        ]


class AddCertificateForm(CertificateForm, VuetifyFormMixin):
    scope_prefix = "cert_data"
    vue_file = "front/src/components/forms/Certificate.vue"
    form_title = '{{ {"S": "Server", "C": "Client", "O": "OCSP"}[this.certtype] }} certificate '
    form_component_name = "Certificate"
    form_object = "certificate"
    vue_card_classes = "elevation-10"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dn_fields = {f"dn.{f}": DistinguishedNameForm().fields[f] for f in DistinguishedNameForm().fields}
        self.fields.update(dn_fields)
        self.fields["passphrase_out"].required = False
        self.fields["passphrase_out_confirmation"].required = False

        self.fields.pop("dn")
        self.fields.pop("parent")
        self.fields.pop("crl_distribution_url")
        self.fields.pop("ocsp_distribution_host")

        self.fields.pop("type")
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        "Distinguished Name",
                        Row(
                            VueSpacer(),
                            Button("reset", "Reset Form", **{"@click": "resetForm"}),
                            Submit("copy", "Copy from Intermediate", **{"@click": "setParentData"}),
                            css_class="mr-1",
                        ),
                        Row(Column("dn.commonName", md="8"), Column("expires_at")),
                        Row(
                            Column(
                                VueField(
                                    "dn.subjectAltNames",
                                    multiple=True,
                                    chips=True,
                                    deletable_chips=True,
                                    append_icon="",
                                ),
                                xs12=True,
                                md12=True,
                            )
                        ),
                        Row(Column("dn.organizationName"), Column("dn.organizationalUnitName", xs12=True, md6=True)),
                        Row(Column("dn.emailAddress", xs12=True, md12=True)),
                        Row(
                            Column("dn.stateOrProvinceName", md="5"),
                            Column("dn.localityName", md="5"),
                            Column("dn.countryName"),
                        ),
                        outlined=True,
                    )
                )
            ),
            Row(
                Column(
                    Fieldset(
                        "Certificate",
                        "name",
                        Row(Column("passphrase_out"), Column("passphrase_out_confirmation")),
                        outlined=True,
                    )
                )
            ),
            Row(
                Column(
                    Fieldset(
                        "Signing credentials",
                        "passphrase_issuer",
                        outlined=True,
                    )
                )
            ),
            ButtonHolder(
                VueSpacer(),
                Button("cancel", "Cancel", **{"@click": "onCancel"}),
                Submit("submit", "Create", **{"@click": "onCreateCertificate", "css_class": "px-6"}),
                css_class="mt-4",
                # TODO BJA outlined=True,
            ),
        )
        self.vue_imports = [("certificates", "../../api/certificates")]
        self.vue_props = ["parent", "certtype"]
        self.vue_watchers = []
        self.vue_extra_initial_statements = """
const date = new Date();
date.setFullYear(date.getFullYear() + 1);
data['certificate']['expires_at'] = date.toISOString().slice(0,10);
        """
        self.vue_methods = [
            """
setParentData() {
    this.certificate.dn.organizationName = this.parent.dn.organizationName;
    this.certificate.dn.stateOrProvinceName = this.parent.dn.stateOrProvinceName;
    this.certificate.dn.countryName = this.parent.dn.countryName;
    this.certificate.dn.localityName = this.parent.dn.localityName;
    this.certificate.dn.organizationalUnitName = this.parent.dn.organizationalUnitName;
    this.certificate.dn.emailAddress = this.parent.dn.emailAddress;
}
            """,
            """
onCreateCertificate() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.passphrase_out_visible = false;
      this.passphrase_out_confirmation_visible = false;
      this.passphrase_in_visible = false;
      this.certificate.type = this.certtype;
      this.certificate.parent = this.parent.id;
      certificates.create(this.certificate).then( response  => {
          this.$emit('update-dasboard');
          this.resetForm();
          this.$emit('close-dialog');
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
        this.$refs.form.$el.scrollIntoView({behavior: 'smooth'});
      });
    }
  });
}
            """,
            """
onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
}
            """,
        ]


class RenewCertificateVueForm(RenewCertificateForm, VuetifyFormMixin):
    scope_prefix = "cert_data"
    vue_file = "front/src/components/forms/RenewCertificate.vue"
    form_title = "Renew certificate ({{this.certrenew.name}})"
    form_component_name = "RenewCertificate"
    form_object = "renew_certificate"
    vue_card_classes = "elevation-10"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["passphrase_out"].required = False
        self.fields["passphrase_out_confirmation"].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        "Renew Certificate",
                        Row(Column("expires_at")),
                        Row(Column(HTML("<h5>Optional Passphrase:</h5>"))),
                        Row(Column("passphrase_out"), Column("passphrase_out_confirmation")),
                        outlined=True,
                    )
                )
            ),
            Row(
                Column(
                    Fieldset(
                        "Signing credentials",
                        "passphrase_issuer",
                        outlined=True,
                    )
                )
            ),
            ButtonHolder(
                VueSpacer(),
                Button("cancel", "Cancel", **{"@click": "onCancel"}),
                Submit("submit", "Renew", **{"@click": "onRenewCertificate", "css_class": "px-6"}),
                css_class="mt-4",
                # TODO BJA outlined=True,
            ),
        )
        self.vue_imports = [("certificates", "../../api/certificates")]
        self.vue_props = ["certrenew"]
        self.vue_watchers = []
        self.vue_extra_initial_statements = """
const date = new Date();
date.setFullYear(date.getFullYear() + 1);
data['renew_certificate']['expires_at'] = date.toISOString().slice(0,10);
        """
        self.vue_methods = [
            """
onRenewCertificate() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.passphrase_out_visible = false;
      this.passphrase_out_confirmation_visible = false;
      this.passphrase_in_visible = false;
      console.log(this.renew_certificate);
      certificates.renew(this.certrenew.id, this.renew_certificate).then( response  => {
          this.$emit('update-dasboard');
          this.resetForm();
          this.$emit('close-dialog');
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
        this.$refs.form.$el.scrollIntoView({behavior: 'smooth'});
      });
    }
  });
}
            """,
            """
onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
}
            """,
        ]


class ChangePasswordForm(SetPasswordForm, VuetifyFormMixin):
    scope_prefix = "user_data"
    vue_file = "front/src/components/forms/user/ChangePassword.vue"
    form_title = "Change Password"
    form_component_name = "changePassword"
    form_object = "password"

    def __init__(self, *args, **kwargs):
        super().__init__(user=None, *args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("new_password1"), Column("new_password2")),
            ButtonHolder(
                VueSpacer(),
                Button("cancel", "Cancel", **{"@click": "onCancel"}),
                Submit("submit", "Update", **{"@click": "updatePassword", "css_class": "px-6"}),
                css_class="mt-4",
            ),
        )
        self.vue_imports = [("profile", "../../../api/profile")]
        self.vue_props = []
        self.vue_watchers = []
        self.vue_methods = [
            """
updatePassword() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.new_password1_visible = false;
      this.new_password1_visible = false;
      profile.changeAccountPassword(this.password).then( response  => {
          this.$emit('success', 'Password has been updated.');
          this.resetForm();
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
      });
    }
  });
}
            """,
            """
onCancel(){
  this.resetForm();
}
            """,
        ]


class ChangeProfileForm(UserChangeForm, VuetifyFormMixin):
    scope_prefix = "profile_data"
    vue_file = "front/src/components/forms/user/ChangeProfile.vue"
    form_title = "Change Profile"
    form_component_name = "changeProfile"
    form_object = "profile"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(VueField("username", disabled=True)),
            ),
            Row(
                Column("first_name"),
                Column("last_name"),
            ),
            Row(
                Column("email"),
            ),
            ButtonHolder(
                VueSpacer(),
                Button("cancel", "Cancel", **{"@click": "onCancel"}),
                Submit("submit", "Update", **{"@click": "updateProfile", "css_class": "px-6"}),
                css_class="mt-4",
            ),
        )
        self.vue_imports = [("profile", "../../../api/profile")]
        self.vue_props = []
        self.vue_watchers = []
        self.vue_mounted = """
    this.resetForm();
    this.setupUserForm();
            """
        self.vue_methods = [
            """
setupUserForm() {
  profile.getAccountDetails()
    .then( response  => {
      this.profile = response.data;
    }).catch((e) => {
      console.log(e);
    });
},
updateProfile() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      const data = {...this.profile};
      delete this.profile['username'];
      profile.updateAccountDetails(this.profile).then( response  => {
          this.resetForm();
          this.setupUserForm();
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
      });
    }
  });
}
            """,
            """
onCancel(){
  this.resetForm();
  this.setupUserForm();
}
            """,
        ]


class AddTokenForm(TokenForm, VuetifyFormMixin):
    scope_prefix = "token_data"
    vue_file = "front/src/components/forms/user/AddToken.vue"
    form_title = "Add Token"
    form_component_name = "addToken"
    form_object = "token"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("name")),
            ButtonHolder(
                VueSpacer(),
                Button("cancel", "Cancel", **{"@click": "onCancel"}),
                Submit("submit", "Add", **{"@click": "createToken", "css_class": "px-6"}),
                css_class="mt-4",
            ),
        )
        self.vue_imports = [("apptokens", "../../../api/apptokens")]
        self.vue_props = []
        self.vue_watchers = []
        self.vue_methods = [
            """
createToken() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.name_visible = false;
      apptokens.create(this.token).then( response  => {
          this.$emit('update-dashboard');
          this.resetForm();
          this.$emit('close-dialog');
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
      });
    }
  });
}
            """,
            """
onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
}
            """,
        ]


class RemoveAccountForm(DeleteAccountForm, VuetifyFormMixin):
    scope_prefix = "user_data"
    vue_file = "front/src/components/forms/user/DeleteAccount.vue"
    form_title = "Delete Account"
    form_component_name = "deleteAccount"
    form_object = "password"

    password = forms.CharField(
        label=_("Password"),
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "password"}),
        help_text=_("Enter your password to confirm account deletion."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    HTML(
                        "Deleting of your account is irreversible. All information associated with your "
                        "account will be permanently deleted, including removal of all your certificates."
                    ),
                )
            ),
            Row(Column("password")),
            ButtonHolder(
                VueSpacer(),
                Button("cancel", "Cancel", **{"@click": "onCancel"}),
                DangerButton("submit", "Delete", **{"@click": "deleteAccount", "css_class": "px-6 darken-2"}),
                css_class="mt-4",
            ),
        )
        self.vue_imports = [("profile", "../../../api/profile")]
        self.vue_props = []
        self.vue_watchers = []
        self.vue_extra_card_objects = """
<v-dialog v-model="dialogDeleteAccount" max-width="565px">
  <v-card>
  <v-card-title class="text-h5">Are you sure you want to delete your account?</v-card-title>
  <v-card-actions>
    <v-spacer></v-spacer>
    <v-btn color="blue darken-1" text @click="closeDialogDeleteAccount">Cancel</v-btn>
    <v-btn color="blue darken-1" text
           @click="deleteAccountConfirm">OK</v-btn>
  </v-card-actions>
  </v-card>
</v-dialog>
        """
        self.vue_extra_initial_statements = """
data['dialogDeleteAccount'] = false;
            """
        self.vue_methods = [
            """
deleteAccount() {
  this.dialogDeleteAccount = true;
},
deleteAccountConfirm() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.password_visible = false;
      profile.deleteAccount(this.password).then( response  => {
          this.$emit('success', 'Account has been deleted.');
          this.resetForm();
          this.closeDialogDeleteAccount();
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
        this.dialogDeleteAccount = false;
      });
    }
  });
},
closeDialogDeleteAccount() {
  this.resetForm();
  this.dialogDeleteAccount = false;
}
            """,
            """
onCancel(){
  this.resetForm();
}
            """,
        ]
