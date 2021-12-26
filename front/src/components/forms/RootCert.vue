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
          <div v-for="error in errors.non_field_errors" :key="error">{{error}}</div>
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

<ValidationProvider name="Common Name" vid="dn__commonName"
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
        <v-col class="" >
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Organization Name" vid="dn__organizationName"
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

<ValidationProvider name="Organization Unit Name" vid="dn__organizationalUnitName"
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

<ValidationProvider name="Email Address" vid="dn__emailAddress"
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

<ValidationProvider name="State or Province Name" vid="dn__stateOrProvinceName"
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

<ValidationProvider name="Locality Name" vid="dn__localityName"
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

<ValidationProvider name="Country" vid="dn__countryName"
                    rules="" v-slot="{ errors }">

<v-select
  v-model="rootcert.dn.countryName"
  :error-messages="errors"
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
    <v-card-text><h5>These services are set in the extensions of the issued certificates</h5><h5>Note: Provide only available services</h5>




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
       @click="onCreateCertificate" color="secondary" dark class=" px-6"
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



function initialState (){
  return {"dialog": false, "passphrase_out_visible": false, "passphrase_out_confirmation_visible": false, "formdata_rootcert_dn_countryName_values": [{"text": "Afghanistan", "value": "AF"}, {"text": "\u00c5land Islands", "value": "AX"}, {"text": "Albania", "value": "AL"}, {"text": "Algeria", "value": "DZ"}, {"text": "American Samoa", "value": "AS"}, {"text": "Andorra", "value": "AD"}, {"text": "Angola", "value": "AO"}, {"text": "Anguilla", "value": "AI"}, {"text": "Antarctica", "value": "AQ"}, {"text": "Antigua and Barbuda", "value": "AG"}, {"text": "Argentina", "value": "AR"}, {"text": "Armenia", "value": "AM"}, {"text": "Aruba", "value": "AW"}, {"text": "Australia", "value": "AU"}, {"text": "Austria", "value": "AT"}, {"text": "Azerbaijan", "value": "AZ"}, {"text": "Bahamas", "value": "BS"}, {"text": "Bahrain", "value": "BH"}, {"text": "Bangladesh", "value": "BD"}, {"text": "Barbados", "value": "BB"}, {"text": "Belarus", "value": "BY"}, {"text": "Belgium", "value": "BE"}, {"text": "Belize", "value": "BZ"}, {"text": "Benin", "value": "BJ"}, {"text": "Bermuda", "value": "BM"}, {"text": "Bhutan", "value": "BT"}, {"text": "Bolivia", "value": "BO"}, {"text": "Bonaire, Sint Eustatius and Saba", "value": "BQ"}, {"text": "Bosnia and Herzegovina", "value": "BA"}, {"text": "Botswana", "value": "BW"}, {"text": "Bouvet Island", "value": "BV"}, {"text": "Brazil", "value": "BR"}, {"text": "British Indian Ocean Territory", "value": "IO"}, {"text": "Brunei", "value": "BN"}, {"text": "Bulgaria", "value": "BG"}, {"text": "Burkina Faso", "value": "BF"}, {"text": "Burundi", "value": "BI"}, {"text": "Cabo Verde", "value": "CV"}, {"text": "Cambodia", "value": "KH"}, {"text": "Cameroon", "value": "CM"}, {"text": "Canada", "value": "CA"}, {"text": "Cayman Islands", "value": "KY"}, {"text": "Central African Republic", "value": "CF"}, {"text": "Chad", "value": "TD"}, {"text": "Chile", "value": "CL"}, {"text": "China", "value": "CN"}, {"text": "Christmas Island", "value": "CX"}, {"text": "Cocos (Keeling) Islands", "value": "CC"}, {"text": "Colombia", "value": "CO"}, {"text": "Comoros", "value": "KM"}, {"text": "Congo", "value": "CG"}, {"text": "Congo (the Democratic Republic of the)", "value": "CD"}, {"text": "Cook Islands", "value": "CK"}, {"text": "Costa Rica", "value": "CR"}, {"text": "C\u00f4te d'Ivoire", "value": "CI"}, {"text": "Croatia", "value": "HR"}, {"text": "Cuba", "value": "CU"}, {"text": "Cura\u00e7ao", "value": "CW"}, {"text": "Cyprus", "value": "CY"}, {"text": "Czechia", "value": "CZ"}, {"text": "Denmark", "value": "DK"}, {"text": "Djibouti", "value": "DJ"}, {"text": "Dominica", "value": "DM"}, {"text": "Dominican Republic", "value": "DO"}, {"text": "Ecuador", "value": "EC"}, {"text": "Egypt", "value": "EG"}, {"text": "El Salvador", "value": "SV"}, {"text": "Equatorial Guinea", "value": "GQ"}, {"text": "Eritrea", "value": "ER"}, {"text": "Estonia", "value": "EE"}, {"text": "Eswatini", "value": "SZ"}, {"text": "Ethiopia", "value": "ET"}, {"text": "Falkland Islands (Malvinas)", "value": "FK"}, {"text": "Faroe Islands", "value": "FO"}, {"text": "Fiji", "value": "FJ"}, {"text": "Finland", "value": "FI"}, {"text": "France", "value": "FR"}, {"text": "French Guiana", "value": "GF"}, {"text": "French Polynesia", "value": "PF"}, {"text": "French Southern Territories", "value": "TF"}, {"text": "Gabon", "value": "GA"}, {"text": "Gambia", "value": "GM"}, {"text": "Georgia", "value": "GE"}, {"text": "Germany", "value": "DE"}, {"text": "Ghana", "value": "GH"}, {"text": "Gibraltar", "value": "GI"}, {"text": "Greece", "value": "GR"}, {"text": "Greenland", "value": "GL"}, {"text": "Grenada", "value": "GD"}, {"text": "Guadeloupe", "value": "GP"}, {"text": "Guam", "value": "GU"}, {"text": "Guatemala", "value": "GT"}, {"text": "Guernsey", "value": "GG"}, {"text": "Guinea", "value": "GN"}, {"text": "Guinea-Bissau", "value": "GW"}, {"text": "Guyana", "value": "GY"}, {"text": "Haiti", "value": "HT"}, {"text": "Heard Island and McDonald Islands", "value": "HM"}, {"text": "Holy See", "value": "VA"}, {"text": "Honduras", "value": "HN"}, {"text": "Hong Kong", "value": "HK"}, {"text": "Hungary", "value": "HU"}, {"text": "Iceland", "value": "IS"}, {"text": "India", "value": "IN"}, {"text": "Indonesia", "value": "ID"}, {"text": "Iran", "value": "IR"}, {"text": "Iraq", "value": "IQ"}, {"text": "Ireland", "value": "IE"}, {"text": "Isle of Man", "value": "IM"}, {"text": "Israel", "value": "IL"}, {"text": "Italy", "value": "IT"}, {"text": "Jamaica", "value": "JM"}, {"text": "Japan", "value": "JP"}, {"text": "Jersey", "value": "JE"}, {"text": "Jordan", "value": "JO"}, {"text": "Kazakhstan", "value": "KZ"}, {"text": "Kenya", "value": "KE"}, {"text": "Kiribati", "value": "KI"}, {"text": "Kuwait", "value": "KW"}, {"text": "Kyrgyzstan", "value": "KG"}, {"text": "Laos", "value": "LA"}, {"text": "Latvia", "value": "LV"}, {"text": "Lebanon", "value": "LB"}, {"text": "Lesotho", "value": "LS"}, {"text": "Liberia", "value": "LR"}, {"text": "Libya", "value": "LY"}, {"text": "Liechtenstein", "value": "LI"}, {"text": "Lithuania", "value": "LT"}, {"text": "Luxembourg", "value": "LU"}, {"text": "Macao", "value": "MO"}, {"text": "Madagascar", "value": "MG"}, {"text": "Malawi", "value": "MW"}, {"text": "Malaysia", "value": "MY"}, {"text": "Maldives", "value": "MV"}, {"text": "Mali", "value": "ML"}, {"text": "Malta", "value": "MT"}, {"text": "Marshall Islands", "value": "MH"}, {"text": "Martinique", "value": "MQ"}, {"text": "Mauritania", "value": "MR"}, {"text": "Mauritius", "value": "MU"}, {"text": "Mayotte", "value": "YT"}, {"text": "Mexico", "value": "MX"}, {"text": "Micronesia (Federated States of)", "value": "FM"}, {"text": "Moldova", "value": "MD"}, {"text": "Monaco", "value": "MC"}, {"text": "Mongolia", "value": "MN"}, {"text": "Montenegro", "value": "ME"}, {"text": "Montserrat", "value": "MS"}, {"text": "Morocco", "value": "MA"}, {"text": "Mozambique", "value": "MZ"}, {"text": "Myanmar", "value": "MM"}, {"text": "Namibia", "value": "NA"}, {"text": "Nauru", "value": "NR"}, {"text": "Nepal", "value": "NP"}, {"text": "Netherlands", "value": "NL"}, {"text": "New Caledonia", "value": "NC"}, {"text": "New Zealand", "value": "NZ"}, {"text": "Nicaragua", "value": "NI"}, {"text": "Niger", "value": "NE"}, {"text": "Nigeria", "value": "NG"}, {"text": "Niue", "value": "NU"}, {"text": "Norfolk Island", "value": "NF"}, {"text": "North Korea", "value": "KP"}, {"text": "North Macedonia", "value": "MK"}, {"text": "Northern Mariana Islands", "value": "MP"}, {"text": "Norway", "value": "NO"}, {"text": "Oman", "value": "OM"}, {"text": "Pakistan", "value": "PK"}, {"text": "Palau", "value": "PW"}, {"text": "Palestine, State of", "value": "PS"}, {"text": "Panama", "value": "PA"}, {"text": "Papua New Guinea", "value": "PG"}, {"text": "Paraguay", "value": "PY"}, {"text": "Peru", "value": "PE"}, {"text": "Philippines", "value": "PH"}, {"text": "Pitcairn", "value": "PN"}, {"text": "Poland", "value": "PL"}, {"text": "Portugal", "value": "PT"}, {"text": "Puerto Rico", "value": "PR"}, {"text": "Qatar", "value": "QA"}, {"text": "R\u00e9union", "value": "RE"}, {"text": "Romania", "value": "RO"}, {"text": "Russia", "value": "RU"}, {"text": "Rwanda", "value": "RW"}, {"text": "Saint Barth\u00e9lemy", "value": "BL"}, {"text": "Saint Helena, Ascension and Tristan da Cunha", "value": "SH"}, {"text": "Saint Kitts and Nevis", "value": "KN"}, {"text": "Saint Lucia", "value": "LC"}, {"text": "Saint Martin (French part)", "value": "MF"}, {"text": "Saint Pierre and Miquelon", "value": "PM"}, {"text": "Saint Vincent and the Grenadines", "value": "VC"}, {"text": "Samoa", "value": "WS"}, {"text": "San Marino", "value": "SM"}, {"text": "Sao Tome and Principe", "value": "ST"}, {"text": "Saudi Arabia", "value": "SA"}, {"text": "Senegal", "value": "SN"}, {"text": "Serbia", "value": "RS"}, {"text": "Seychelles", "value": "SC"}, {"text": "Sierra Leone", "value": "SL"}, {"text": "Singapore", "value": "SG"}, {"text": "Sint Maarten (Dutch part)", "value": "SX"}, {"text": "Slovakia", "value": "SK"}, {"text": "Slovenia", "value": "SI"}, {"text": "Solomon Islands", "value": "SB"}, {"text": "Somalia", "value": "SO"}, {"text": "South Africa", "value": "ZA"}, {"text": "South Georgia and the South Sandwich Islands", "value": "GS"}, {"text": "South Korea", "value": "KR"}, {"text": "South Sudan", "value": "SS"}, {"text": "Spain", "value": "ES"}, {"text": "Sri Lanka", "value": "LK"}, {"text": "Sudan", "value": "SD"}, {"text": "Suriname", "value": "SR"}, {"text": "Svalbard and Jan Mayen", "value": "SJ"}, {"text": "Sweden", "value": "SE"}, {"text": "Switzerland", "value": "CH"}, {"text": "Syria", "value": "SY"}, {"text": "Taiwan", "value": "TW"}, {"text": "Tajikistan", "value": "TJ"}, {"text": "Tanzania", "value": "TZ"}, {"text": "Thailand", "value": "TH"}, {"text": "Timor-Leste", "value": "TL"}, {"text": "Togo", "value": "TG"}, {"text": "Tokelau", "value": "TK"}, {"text": "Tonga", "value": "TO"}, {"text": "Trinidad and Tobago", "value": "TT"}, {"text": "Tunisia", "value": "TN"}, {"text": "Turkey", "value": "TR"}, {"text": "Turkmenistan", "value": "TM"}, {"text": "Turks and Caicos Islands", "value": "TC"}, {"text": "Tuvalu", "value": "TV"}, {"text": "Uganda", "value": "UG"}, {"text": "Ukraine", "value": "UA"}, {"text": "United Arab Emirates", "value": "AE"}, {"text": "United Kingdom", "value": "GB"}, {"text": "United States Minor Outlying Islands", "value": "UM"}, {"text": "United States of America", "value": "US"}, {"text": "Uruguay", "value": "UY"}, {"text": "Uzbekistan", "value": "UZ"}, {"text": "Vanuatu", "value": "VU"}, {"text": "Venezuela", "value": "VE"}, {"text": "Vietnam", "value": "VN"}, {"text": "Virgin Islands (British)", "value": "VG"}, {"text": "Virgin Islands (U.S.)", "value": "VI"}, {"text": "Wallis and Futuna", "value": "WF"}, {"text": "Western Sahara", "value": "EH"}, {"text": "Yemen", "value": "YE"}, {"text": "Zambia", "value": "ZM"}, {"text": "Zimbabwe", "value": "ZW"}], "rootcert": {"name": "", "expires_at": null, "crl_distribution_url": "", "ocsp_distribution_host": "", "passphrase_out": "", "passphrase_out_confirmation": "", "dn": {"commonName": "", "subjectAltNames": [], "organizationName": "", "organizationalUnitName": "", "emailAddress": "", "countryName": null, "stateOrProvinceName": "", "localityName": ""}}}
}

export default {
    name: 'RootCert',
    props: [],
    data() {
        return initialState();
    },
    watch: {
      
    },
    mounted() {
       
    },
    methods: {
    resetForm: function (){
        Object.assign(this.$data, initialState());
        this.$refs.form.reset();
        
    },

    
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
            ,

    
onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
}
            ,

},

};

</script>
