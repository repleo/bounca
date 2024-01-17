<template>
<!-- eslint-disable -->
<!-- Generated with django-vuetifyforms -->
<v-card class="elevation-10">
  <v-toolbar dark flat color="primary" class="mb-6">
    <v-toolbar-title>Renew certificate ({{this.certrenew.name}})</v-toolbar-title>
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
<v-card-title class="headline">Renew Certificate</v-card-title>
    <v-card-text><v-row class="" >
        <v-col class="" >





<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Expires at" vid="expires_at"
                    rules="required" v-slot="{ errors }">

<v-text-field
  label="Expires at*"
  v-model="renew_certificate.expires_at"
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
        <h5>Optional Passphrase:</h5>
</v-col>

</v-row>
<v-row class="" >
        <v-col class="" >





<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Passphrase" vid="passphrase_out"
                    rules="" v-slot="{ errors }">

<v-text-field
  label="Passphrase"
  v-model="renew_certificate.passphrase_out"
  :error-messages="errors"

  :append-icon="passphrase_out_visible ? 'visibility' : 'visibility_off'"
  @click:append="() => (passphrase_out_visible = !passphrase_out_visible)"
  :type="passphrase_out_visible ? 'text' : 'password' "




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
                    rules="confirmed:passphrase_out" v-slot="{ errors }">

<v-text-field
  label="Passphrase confirmation"
  v-model="renew_certificate.passphrase_out_confirmation"
  :error-messages="errors"

  :append-icon="passphrase_out_confirmation_visible ? 'visibility' : 'visibility_off'"
  @click:append="() => (passphrase_out_confirmation_visible = !passphrase_out_confirmation_visible)"
  :type="passphrase_out_confirmation_visible ? 'text' : 'password' "




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
<v-row class="" >
        <v-col class="" >
        <v-card class=" "  outlined>
<v-card-title class="headline">Signing credentials</v-card-title>
    <v-card-text>




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Passphrase issuer" vid="passphrase_issuer"
                    rules="required" v-slot="{ errors }">

<v-text-field
  label="Passphrase issuer*"
  v-model="renew_certificate.passphrase_issuer"
  :error-messages="errors"

  :append-icon="passphrase_issuer_visible ? 'visibility' : 'visibility_off'"
  @click:append="() => (passphrase_issuer_visible = !passphrase_issuer_visible)"
  :type="passphrase_issuer_visible ? 'text' : 'password' "

  required


  v-bind="attrs"
  v-on="on"

></v-text-field>



</ValidationProvider>

</template>
<span>The passphrase for unlocking your signing key.</span>
</v-tooltip>



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
       @click="onRenewCertificate" color="secondary" dark class=" px-6"
>
    Renew
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
  const data = {"dialog": false, "passphrase_issuer_visible": false, "passphrase_out_visible": false, "passphrase_out_confirmation_visible": false, "renew_certificate": {"expires_at": null, "passphrase_issuer": "", "passphrase_out": "", "passphrase_out_confirmation": ""}};

const date = new Date();
date.setFullYear(date.getFullYear() + 1);
data['renew_certificate']['expires_at'] = date.toISOString().slice(0,10);

  return data;
}

export default {
    name: 'RenewCertificate',
    props: ['certrenew'],
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


onRenewCertificate() {
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.passphrase_out_visible = false;
      this.passphrase_out_confirmation_visible = false;
      this.passphrase_in_visible = false;
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
            ,


onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
}
            ,

},

};

</script>
