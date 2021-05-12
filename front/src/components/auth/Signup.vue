<template>
  <v-layout align-center justify-center>
    <v-flex xs12 sm8 md4>
      <v-card class="elevation-10">
        <v-toolbar dark flat color="primary">
          <v-toolbar-title>Sign up</v-toolbar-title>
        </v-toolbar>
        <v-card-text>
          <v-alert
              text
              border="left"
              colored-border
              type="info"
              v-if="authenticated || detail"
            >
            <div v-if="authenticated">You are already logged in! You don't need to register.</div>
            <div v-else>{{detail}}</div>
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
            <ValidationProvider name="username" vid="username"
                                rules="required" v-slot="{ errors }">
            <v-text-field
              prepend-icon="person"
              label="Username"
              v-model="subscription.username"
              :error-messages="errors"
              type="text"
              required
            ></v-text-field>
            </ValidationProvider>
            <ValidationProvider name="email" vid="email" rules="required|email" v-slot="{ errors }">
            <v-text-field
              prepend-icon="email"
              name="email"
              label="Email address"
              id="email"
              v-model="subscription.email"
              :error-messages="errors"
              required
            ></v-text-field>
            </ValidationProvider>
            <ValidationProvider name="password" vid="password1"
                                rules="required" v-slot="{ errors }">
            <v-text-field
              prepend-icon="lock"
              name="password1"
              label="Password"
              id="password1"
              v-model="subscription.password1"
              :error-messages="errors"
              :append-icon="password1_visible ? 'visibility' : 'visibility_off'"
              @click:append="() => (password1_visible = !password1_visible)"
              :type="password1_visible ? 'text' : 'password' "
              required
            ></v-text-field>
            </ValidationProvider>
            <ValidationProvider name="password" vid="password2"
                                rules="required|confirmed:password1" v-slot="{ errors }">
            <v-text-field
              prepend-icon="lock"
              name="password2"
              label="Password (confirm)"
              id="password2"
              v-model="subscription.password2"
              :error-messages="errors"
              :append-icon="password2_visible ? 'visibility' : 'visibility_off'"
              @click:append="() => (password2_visible = !password2_visible)"
              :type="password2_visible ? 'text' : 'password' "
              required
            ></v-text-field>
            </ValidationProvider>
          </v-form>
          </ValidationObserver>
        </v-card-text>
        <v-card-actions class="mr-2 pb-4" v-if="!authenticated">
          <v-btn
            color="darkgrey"
            plain
            text
            :to="{ name: 'auth_login'}"
          >
            sign in?
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            dark
            color="secondary"
            class="px-4"
            @click="register"
            v-if="!detail"
          >
            Register
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
import auth from '../../api/auth';

export default {
  name: 'Signup',
  data() {
    return {
      // TODO get authentication information
      authenticated: false,
      subscription: {
        username: '',
        password1: '',
        password2: '',
        email: '',
      },
      detail: '',
      password1_visible: false,
      password2_visible: false,
    };
  },
  methods: {
    register() {
      this.$refs.form.validate().then((isValid) => {
        if (isValid) {
          // ensure password vaults dont recognize password fields as user
          this.password1_visible = false;
          this.password2_visible = false;
          auth.createAccount(this.subscription).then((response) => {
            if ('detail' in response.data) {
              this.detail = response.data.detail;
            } else {
              // this.$store.dispatch('login', response.data.key);
              // this.$router.push('/');
            }
          }).catch((r) => {
            this.$refs.form.setErrors(r.response.data);
          });
        }
      });
    },
  },
};
</script>
