<template>
  <v-layout align-center justify-center>
    <v-flex xs12 sm8 md4>
      <ValidationObserver ref="form" v-slot="{ errors }">
      <v-card class="elevation-10">
        <v-toolbar dark flat color="primary">
          <v-toolbar-title>Enter new password</v-toolbar-title>
        </v-toolbar>
        <v-card-text v-if="detail">
          <v-alert
              text
              dense
              color="info"
              icon="mdi-alert-octagon-outline"
              border="left"
              v-if="detail"
          >
            <div>{{detail}}</div>
          </v-alert>        </v-card-text>
        <v-card-text v-else>
          <ValidationProvider name="token_errors" vid="token_errors">
            <v-alert
              text
              dense
              color="error"
              icon="mdi-alert-octagon-outline"
              border="left"
              v-if="errors.token_errors && errors.token_errors.length"
            >
            <div v-for="error in errors.token_errors" :key="error">{{error}}</div>
            </v-alert>
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
          <v-form v-if="!(errors.token_errors && errors.token_errors.length)">
            <ValidationProvider name="password" vid="new_password1"
                                rules="required" v-slot="{ errors }">
            <v-text-field
              prepend-icon="lock"
              name="new_password1"
              label="Password"
              id="new_password1"
              v-model="credentials.new_password1"
              :error-messages="errors"
              :append-icon="password1_visible ? 'visibility' : 'visibility_off'"
              @click:append="() => (password1_visible = !password1_visible)"
              :type="password1_visible ? 'text' : 'password' "
              required
            ></v-text-field>
            </ValidationProvider>
            <ValidationProvider name="password" vid="new_password2"
                                rules="required|confirmed:new_password1" v-slot="{ errors }">
            <v-text-field
              prepend-icon="lock"
              name="new_password2"
              label="Password (confirm)"
              id="new_password2"
              v-model="credentials.new_password2"
              :error-messages="errors"
              :append-icon="password2_visible ? 'visibility' : 'visibility_off'"
              @click:append="() => (password2_visible = !password2_visible)"
              :type="password2_visible ? 'text' : 'password' "
              required
            ></v-text-field>
            </ValidationProvider>
          </v-form>
        </v-card-text>
        <v-card-actions class="mr-2 pb-4">
          <v-btn
            color="darkgrey"
            plain
            text
            :to="{ name: 'auth_login'}"
          >
            Sign in?
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            dark
            color="secondary"
            class="px-4"
            @click="passwordForgot"
            v-if="!(detail || (errors.token_errors && errors.token_errors.length))"
          >
            Reset
          </v-btn>
        </v-card-actions>
      </v-card>
      </ValidationObserver>
    </v-flex>
  </v-layout>
</template>

<script>
import auth from '../../api/auth';

export default {
  name: 'AuthPasswordReset',
  data() {
    return {
      credentials: {
        new_password1: '',
        new_password2: '',
        uid: '',
        token: '',
      },
      password1_visible: false,
      password2_visible: false,
      detail: '',
      errors: {},
    };
  },
  methods: {
    passwordForgot() {
      this.$refs.form.validate().then((isValid) => {
        if (isValid) {
          const payload = Object.assign(this.credentials, this.$route.params);
          this.password1_visible = false; // ensure password vaults dont see password fields as user
          this.password2_visible = false;
          auth.resetAccountPassword(payload).then((response) => {
            this.detail = response.data.detail;
          }).catch((r) => {
            if ('token' in r.response.data) {
              this.$refs.form.setErrors({
                token_errors: ['Token invalid, please start new password reset request.'],
              });
            } else {
              this.$refs.form.setErrors(r.response.data);
            }
          });
        }
      });
    },
  },
};
</script>
