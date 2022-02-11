<template>
<!-- eslint-disable -->
<!-- Generated with django-vuetifyforms -->
<v-card >
  <v-toolbar dark flat color="primary" class="mb-6">
    <v-toolbar-title>Change Password</v-toolbar-title>
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
        




<v-tooltip bottom>
<template v-slot:activator="{ on, attrs }">

<ValidationProvider name="New password" vid="new_password1"
                    rules="required" v-slot="{ errors }">

<v-text-field
  label="New password*"
  v-model="password.new_password1"
  :error-messages="errors"
  
  :append-icon="new_password1_visible ? 'visibility' : 'visibility_off'"
  @click:append="() => (new_password1_visible = !new_password1_visible)"
  :type="new_password1_visible ? 'text' : 'password' "
  
  required
  
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span><ul><li>Your password can’t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can’t be a commonly used password.</li><li>Your password can’t be entirely numeric.</li></ul></span>
</v-tooltip>




</v-col>
<v-col class="" >
        




<ValidationProvider name="New password confirmation" vid="new_password2"
                    rules="required" v-slot="{ errors }">

<v-text-field
  label="New password confirmation*"
  v-model="password.new_password2"
  :error-messages="errors"
  
  :append-icon="new_password2_visible ? 'visibility' : 'visibility_off'"
  @click:append="() => (new_password2_visible = !new_password2_visible)"
  :type="new_password2_visible ? 'text' : 'password' "
  
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
       @click="updatePassword" color="secondary" dark class=" px-6"
>
    Update
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
  return {"dialog": false, "new_password1_visible": false, "new_password2_visible": false, "password": {"new_password1": "", "new_password2": ""}}
}

export default {
    name: 'changePassword',
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
            ,

    
onCancel(){
  this.resetForm();
}
            ,

},

};

</script>
