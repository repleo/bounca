<template>
<!-- eslint-disable -->
<!-- Generated with django-vuetifyforms -->
<v-card >
  <v-toolbar dark flat color="primary" class="mb-6">
    <v-toolbar-title>Delete Account</v-toolbar-title>
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
        Deleting of your account is irreversible. All information associated with your account will be permanently deleted, including removal of all your certificates.
</v-col>

</v-row>
<v-row class="" >
        <v-col class="" >
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="Password" vid="password"
                    rules="required" v-slot="{ errors }">

<v-text-field
  label="Password*"
  v-model="password.password"
  :error-messages="errors"
  
  :append-icon="password_visible ? 'visibility' : 'visibility_off'"
  @click:append="() => (password_visible = !password_visible)"
  :type="password_visible ? 'text' : 'password' "
  
  required
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>Enter your password to confirm account deletion.</span>
</v-tooltip>




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
       @click="deleteAccount" color="red" dark class=" px-6 darken-2"
>
    Delete
</v-btn>

</v-card-actions>





    </v-form>
    </ValidationObserver>
  </v-card-text>
  
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
        
</v-card>
</template>


<script>


import profile from '../../../api/profile';



function initialState (){
  const data = {"dialog": false, "password_visible": false, "password": {"password": ""}};
  
data['dialogDeleteAccount'] = false;
            
  return data;
}

export default {
    name: 'deleteAccount',
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
            ,

    
onCancel(){
  this.resetForm();
}
            ,

},

};

</script>
