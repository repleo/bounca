<template>
<!-- eslint-disable -->
<!-- Generated with django-vuetifyforms -->
<v-card class="elevation-10">
  <v-toolbar dark flat color="primary" class="mb-6">
    <v-toolbar-title>Root Certificate</v-toolbar-title>
  </v-toolbar>
  <v-card-text>
  <ValidationObserver ref="form" v-slot="{ errors }">
    <v-form>
      <ValidationProvider name="non_field_errors" vid="non_field_errors">
        <v-alert
          text
          dense
          color="error"
          icon="mdi-alert-octagon-outline"
          border="left"
          v-if="errors.non_field_errors && errors.non_field_errors.length"
          >
          <div v-for="error in errors.non_field_errors" :key="error"></div>
        </v-alert>
      </ValidationProvider>

      
    
    <v-row class="" >
        <v-col class="" >
        <v-card class=" "  outlined>
<v-card-title class="headline">Distinguished Name</v-card-title>
    <v-card-text><v-row class="" >
        <v-col class=""  md="8">
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Common Name" vid="dn.commonName"
                    rules="max:64|required" v-slot="{ errors }">

<v-text-field
  label="Common Name*"
  v-model="rootcert.dn.commonName"
  :error-messages="errors"
  
  type="text"
  
  required
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>The fully qualified domain name (FQDN) of your server. This must match exactly what you type in your web browser or you will receive a name mismatch error.</span>
</v-tooltip>




</v-col>
<v-col class="" >
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Expires at" vid="expires_at"
                    rules="required" v-slot="{ errors }">

<v-text-field
  label="Expires at*"
  v-model="rootcert.expires_at"
  :error-messages="errors"
  
  type="date"
  
  required
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>Select the date that the certificate will expire: for root typically 20 years, for intermediate 10 years for other types 1 year.</span>
</v-tooltip>




</v-col>

</v-row>
<v-row class="" >
        <v-col class=""  md12 xs12>
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="SubjectAltNames" vid="dn.subjectAltNames"
                    rules="" v-slot="{ errors }">

<v-combobox
  v-model="rootcert.dn.subjectAltNames"
  label="SubjectAltNames"
   chips="True" deletable-chips="True" multiple="True"
></v-combobox>



</ValidationProvider>

</template>
<span>subjectAltName list, i.e. dns names for server certs and email adresses for client certs. (separate by comma)</span>
</v-tooltip>




</v-col>

</v-row>
<v-row class="" >
        <v-col class="" >
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Organization Name" vid="dn.organizationName"
                    rules="max:64" v-slot="{ errors }">

<v-text-field
  label="Organization Name"
  v-model="rootcert.dn.organizationName"
  :error-messages="errors"
  
  type="text"
  
  
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>The legal name of your organization. This should not be abbreviated and should include suffixes such as Inc, Corp, or LLC.</span>
</v-tooltip>




</v-col>
<v-col class=""  md6 xs12>
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Organization Unit Name" vid="dn.organizationalUnitName"
                    rules="max:64" v-slot="{ errors }">

<v-text-field
  label="Organization Unit Name"
  v-model="rootcert.dn.organizationalUnitName"
  :error-messages="errors"
  
  type="text"
  
  
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>The division of your organization handling the certificate.</span>
</v-tooltip>




</v-col>

</v-row>
<v-row class="" >
        <v-col class=""  md12 xs12>
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Email Address" vid="dn.emailAddress"
                    rules="email|max:64" v-slot="{ errors }">

<v-text-field
  label="Email Address"
  v-model="rootcert.dn.emailAddress"
  :error-messages="errors"
  
  type="email"
  
  
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>The email address to contact your organization.</span>
</v-tooltip>




</v-col>

</v-row>
<v-row class="" >
        <v-col class=""  md="5">
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="State or Province Name" vid="dn.stateOrProvinceName"
                    rules="max:128" v-slot="{ errors }">

<v-text-field
  label="State or Province Name"
  v-model="rootcert.dn.stateOrProvinceName"
  :error-messages="errors"
  
  type="text"
  
  
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>The state/region where your organization is located. This shouldn't be abbreviated. (1–128 characters)</span>
</v-tooltip>




</v-col>
<v-col class=""  md="5">
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Locality Name" vid="dn.localityName"
                    rules="max:128" v-slot="{ errors }">

<v-text-field
  label="Locality Name"
  v-model="rootcert.dn.localityName"
  :error-messages="errors"
  
  type="text"
  
  
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>The city where your organization is located. (1–128 characters)</span>
</v-tooltip>




</v-col>
<v-col class="" >
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Country" vid="dn.countryName"
                    rules="" v-slot="{ errors }">

<v-select
  v-model="rootcert.dn.countryName"
  :items="formdata_rootcert_dn_countryName_values"
  label="Country"
  
></v-select>



</ValidationProvider>

</template>
<span>The two-character country name in ISO 3166 format.</span>
</v-tooltip>




</v-col>

</v-row>
</v-card-text>
</v-card>

</v-col>

</v-row>
<v-row class="" >
        <v-col class="" >
        <v-card class=" "  outlined>
<v-card-title class="headline">Revocation Services</v-card-title>
    <v-card-text>




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="CRL distribution url" vid="crl_distribution_url"
                    rules="url|max:200" v-slot="{ errors }">

<v-text-field
  label="CRL distribution url"
  v-model="rootcert.crl_distribution_url"
  :error-messages="errors"
  
  type="url"
  
  
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>Base URL for certificate revocation list (CRL)</span>
</v-tooltip>








<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="OCSP distribution host" vid="ocsp_distribution_host"
                    rules="url|max:200" v-slot="{ errors }">

<v-text-field
  label="OCSP distribution host"
  v-model="rootcert.ocsp_distribution_host"
  :error-messages="errors"
  
  type="url"
  
  
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>Host URL for Online Certificate Status Protocol (OCSP)</span>
</v-tooltip>



</v-card-text>
</v-card>

</v-col>

</v-row>
<v-row class="" >
        <v-col class="" >
        <v-card class=" "  outlined>
<v-card-title class="headline">Certificate</v-card-title>
    <v-card-text>




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Name" vid="name"
                    rules="max:128" v-slot="{ errors }">

<v-text-field
  label="Name"
  v-model="rootcert.name"
  :error-messages="errors"
  
  type="text"
  
  
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>Name of your key, if not set will be equal to your CommonName.</span>
</v-tooltip>



<v-row class="" >
        <v-col class="" >
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Passphrase" vid="passphrase_out"
                    rules="required" v-slot="{ errors }">

<v-text-field
  label="Passphrase*"
  v-model="rootcert.passphrase_out"
  :error-messages="errors"
  
  :append-icon="passphrase_out_visible ? 'visibility' : 'visibility_off'"
  @click:append="() => (passphrase_out_visible = !passphrase_out_visible)"
  :type="passphrase_out_visible ? 'text' : 'password' "
  
  required
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>Passphrase for protecting the key of your new certificate.</span>
</v-tooltip>




</v-col>
<v-col class="" >
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Passphrase confirmation" vid="passphrase_out_confirmation"
                    rules="confirmed:passphrase_out|required" v-slot="{ errors }">

<v-text-field
  label="Passphrase confirmation*"
  v-model="rootcert.passphrase_out_confirmation"
  :error-messages="errors"
  
  :append-icon="passphrase_out_confirmation_visible ? 'visibility' : 'visibility_off'"
  @click:append="() => (passphrase_out_confirmation_visible = !passphrase_out_confirmation_visible)"
  :type="passphrase_out_confirmation_visible ? 'text' : 'password' "
  
  required
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>Enter the same passphrase as before, for verification.</span>
</v-tooltip>




</v-col>

</v-row>
</v-card-text>
</v-card>

</v-col>

</v-row>
<v-card-actions class="mt-4" >
       <v-spacer></v-spacer>
<v-btn
       @click="onCancel" color="primary" plain text 
>
    Cancel
</v-btn>
<v-btn
       @click="onCcreateCertificate" color="secondary" dark class=" px-6"
>
    Create
</v-btn>

</v-card-actions>





    </v-form>
    </ValidationObserver>
  </v-card-text>

</v-card>
</template>


<script>


import certificates from '../../api/certificates';



export default {
    name: 'Root Certificate',

    data() {
        return {"dialog": false, "passphrase_out_visible": false, "passphrase_out_confirmation_visible": false, "formdata_rootcert_dn_countryName_values": ["Afghanistan", "\u00c5land Islands", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bonaire, Sint Eustatius and Saba", "Bosnia and Herzegovina", "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Cayman Islands", "Central African Republic", "Chad", "Chile", "China", "Christmas Island", "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo", "Congo (the Democratic Republic of the)", "Cook Islands", "Costa Rica", "C\u00f4te d'Ivoire", "Croatia", "Cuba", "Cura\u00e7ao", "Cyprus", "Czechia", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Falkland Islands (Malvinas)", "Faroe Islands", "Fiji", "Finland", "France", "French Guiana", "French Polynesia", "French Southern Territories", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Heard Island and McDonald Islands", "Holy See", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macao", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico", "Micronesia (Federated States of)", "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island", "North Korea", "North Macedonia", "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestine, State of", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn", "Poland", "Portugal", "Puerto Rico", "Qatar", "R\u00e9union", "Romania", "Russia", "Rwanda", "Saint Barth\u00e9lemy", "Saint Helena, Ascension and Tristan da Cunha", "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin (French part)", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Sint Maarten (Dutch part)", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Georgia and the South Sandwich Islands", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Svalbard and Jan Mayen", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks and Caicos Islands", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States Minor Outlying Islands", "United States of America", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Virgin Islands (British)", "Virgin Islands (U.S.)", "Wallis and Futuna", "Western Sahara", "Yemen", "Zambia", "Zimbabwe"], "rootcert": {"name": "", "expires_at": null, "crl_distribution_url": "", "ocsp_distribution_host": "", "passphrase_out": "", "passphrase_out_confirmation": "", "dn": {"commonName": "", "subjectAltNames": "", "organizationName": "", "organizationalUnitName": "", "emailAddress": "", "countryName": null, "stateOrProvinceName": "", "localityName": ""}}};
    },
methods: {

  
onCcreateCertificate() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.passphrase_out_visible = false;
      this.passphrase_out_confirmation_visible = false;
      certificates.createAccount(this.rootcert).then((response) => {
          // this.$store.dispatch('login', response.data.key);
          // this.$router.push('/');

      }).catch((r) => {
        this.$refs.form.setErrors(r.response.data);
      });
    }
  });
}               ,

  
onCancel(){
  console.log('CANCEL SUBMIT');
  this.$emit('close-dialog');
}
                ,

},

};

</script>
