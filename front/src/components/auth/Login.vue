<template>
  <v-layout align-center justify-center>
    <v-flex xs12 sm8 md4>
      <v-card class="elevation-10">
        <v-toolbar dark flat color="primary">
          <v-toolbar-title>Login</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn
            dark
            color="blue lighten-1"
            class="px-2"
            :to="{ name: 'auth_signup'}"
          >
            Sign Up
          </v-btn>
        </v-toolbar>
        <v-card-text>
          <ValidationObserver ref="form" v-slot="{ errors }">
          <ValidationProvider name="non_field_errors" vid="non_field_errors">
            <v-alert
              text
              dense
              type="error"
              border="left"
              v-if="errors.non_field_errors && errors.non_field_errors.length"
            >
            <div v-for="error in errors.non_field_errors" :key="error">{{error}}</div>
            </v-alert>
          </ValidationProvider>
          <v-form>
            <ValidationProvider name="username or e-mail" vid="usernameOrEmail"
                                rules="required" v-slot="{ errors }">
            <v-text-field
              prepend-icon="person"
              label="Username or e-mail address"
              v-model="usernameOrEmail"
              :error-messages="errors"
              type="text"
              required
            ></v-text-field>
            </ValidationProvider>
            <ValidationProvider name="password" vid="password" rules="required" v-slot="{ errors }">
            <v-text-field
              prepend-icon="lock"
              name="password"
              label="Password"
              id="password"
              v-model="credentials.password"
              :error-messages="errors"
              :append-icon="password_visible ? 'visibility' : 'visibility_off'"
              @click:append="() => (password_visible = !password_visible)"
              :type="password_visible ? 'text' : 'password' "
              required
            ></v-text-field>
            </ValidationProvider>
          </v-form>
          </ValidationObserver>
        </v-card-text>
        <v-card-actions class="mr-2 pb-4">
          <v-btn
            color="darkgrey"
            plain
            text
            :to="{ name: 'auth_password_forgot'}"
          >
            Forgot Password
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            dark
            color="secondary"
            class="px-4"
            @click="login"
          >
            Login
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
export default {
  name: 'AuthLogin',
  data() {
    return {
      usernameOrEmail: null,
      credentials: {
        password: null,
      },
      password_visible: false,
    };
  },
  methods: {
    login() {
      this.$refs.form.validate().then((isValid) => {
        if (isValid) {
          if (/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(this.usernameOrEmail)) {
            this.credentials.email = this.usernameOrEmail;
            delete this.credentials.username;
          } else {
            delete this.credentials.email;
            this.credentials.username = this.usernameOrEmail;
          }
          this.$store.dispatch('auth/login', this.credentials)
            .then(() => this.$router.push('/dashboard'))
            .catch((r) => {
              const errors = r.response.data;
              errors.usernameOrEmail = errors.username + errors.email;
              this.$refs.form.setErrors(errors);
            });
        }
      });
    },
  },
};
</script>
