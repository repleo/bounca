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
        




<ValidationProvider name="Password" vid="password"
                    rules="max:128|required" v-slot="{ errors }">

<v-text-field
  label="Password*"
  v-model="password.password"
  :error-messages="errors"
  
  type="text"
  
  required
  
  
></v-text-field>



</ValidationProvider>




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

</v-card>
</template>


<script>


import profile from '../../../api/profile';



function initialState (){
  const data = {"dialog": false, "password": {"password": ""}};
  
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
  this.$refs.form.validate().then((isValid) => {
    if (isValid) {
      this.password_visible = false;
      profile.deleteAccountPassword(this.password).then( response  => {
          this.$emit('success', 'Password has been updated.');
          this.resetForm();
      }).catch( r => {
        this.$refs.form.setErrors(r.response.data);
      });
    }
  });
}
            ,

    
onCancel(){
  this.resetForm();
}
            ,

},

};

</script>
