<template>
  <v-card-text>
    <v-alert
        text
        dense
        color="info"
        icon="mdi-alert-octagon-outline"
        border="left"
        v-if="detail"
    >
      <div>{{detail}}</div>
    </v-alert>
    <ValidationObserver v-else ref="form" v-slot="{ errors }">
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
    <v-form>
      <ValidationProvider name="email" vid="email" rules="required|email" v-slot="{ errors }">
      <v-text-field
        prepend-icon="email"
        name="email"
        label="Email address"
        id="email"
        v-model="email"
        :error-messages="errors"
        required
      ></v-text-field>
      </ValidationProvider>
    </v-form>
    </ValidationObserver>
  </v-card-text>
</template>

<script>
import auth from '../../api/auth';

export default {
  name: 'passwordForgot',
  data() {
    return {
      email: '',
      detail: '',
      errors: {},
    };
  },
  methods: {
    passwordForgot() {
      this.$refs.form.validate().then((isValid) => {
        if (isValid) {
          auth.sendAccountPasswordResetEmail({ email: this.email }).then((response) => {
            this.detail = response.data.detail;
          }).catch((r) => {
            this.$refs.form.setErrors(r.response.data);
          });
        }
      });
    },
  },
};
</script>
