<template>
<!-- eslint-disable -->
<!-- Generated with django-vuetifyforms -->
<v-card >
  <v-toolbar dark flat color="primary" class="mb-6">
    <v-toolbar-title>Add Token</v-toolbar-title>
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
        




<ValidationProvider name="Name" vid="name"
                    rules="required" v-slot="{ errors }">

<v-text-field
  label="Name*"
  v-model="token.name"
  :error-messages="errors"
  
  type="textarea"
  
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
       @click="createToken" color="secondary" dark class=" px-6"
>
    Add
</v-btn>

</v-card-actions>





    </v-form>
    </ValidationObserver>
  </v-card-text>
  
</v-card>
</template>


<script>


import apptokens from '../../../api/apptokens';



function initialState (){
  const data = {"dialog": false, "token": {"name": ""}};
  
  return data;
}

export default {
    name: 'addToken',
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
            ,

    
onCancel(){
  this.resetForm();
  this.$emit('close-dialog');
}
            ,

},

};

</script>
