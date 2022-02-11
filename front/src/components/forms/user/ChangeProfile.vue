<template>
<!-- eslint-disable -->
<!-- Generated with django-vuetifyforms -->
<v-card >
  <v-toolbar dark flat color="primary" class="mb-6">
    <v-toolbar-title>Change Profile</v-toolbar-title>
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

<ValidationProvider name="Username" vid="username"
                    rules="max:150|required" v-slot="{ errors }">

<v-text-field
  label="Username*"
  v-model="profile.username"
  :error-messages="errors"
  
  type="text"
  
  required
   disabled
  
  v-bind="attrs"
  v-on="on"
  
></v-text-field>



</ValidationProvider>

</template>
<span>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</span>
</v-tooltip>




</v-col>

</v-row>
<v-row class="" >
        <v-col class="" >
        




<ValidationProvider name="First name" vid="first_name"
                    rules="max:150" v-slot="{ errors }">

<v-text-field
  label="First name"
  v-model="profile.first_name"
  :error-messages="errors"
  
  type="text"
  
  
  
  
></v-text-field>



</ValidationProvider>




</v-col>
<v-col class="" >
        




<ValidationProvider name="Last name" vid="last_name"
                    rules="max:150" v-slot="{ errors }">

<v-text-field
  label="Last name"
  v-model="profile.last_name"
  :error-messages="errors"
  
  type="text"
  
  
  
  
></v-text-field>



</ValidationProvider>




</v-col>

</v-row>
<v-row class="" >
        <v-col class="" >
        




<ValidationProvider name="Email address" vid="email"
                    rules="email|max:254" v-slot="{ errors }">

<v-text-field
  label="Email address"
  v-model="profile.email"
  :error-messages="errors"
  
  type="email"
  
  
  
  
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
       @click="updateProfile" color="secondary" dark class=" px-6"
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
  return {"dialog": false, "profile": {"password": null, "last_login": null, "is_superuser": null, "groups": null, "user_permissions": null, "username": "", "first_name": "", "last_name": "", "email": "", "is_staff": null, "is_active": null, "date_joined": null}}
}

export default {
    name: 'changeProfile',
    props: [],
    data() {
        return initialState();
    },
    watch: {
      
    },
    mounted() {
       
    this.resetForm();
    this.setupUserForm();
            
    },
    methods: {
    resetForm: function (){
        Object.assign(this.$data, initialState());
        this.$refs.form.reset();
        
    },

    
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
            ,

    
onCancel(){
  this.resetForm();
  this.setupUserForm();
}
            ,

},

};

</script>
