<template>
  <v-layout align-center justify-center>
    <v-flex xs12 sm8 md4>
      <v-card class="elevation-10">
        <v-toolbar dark flat color="primary">
          <v-toolbar-title>Verify e-mail</v-toolbar-title>
        </v-toolbar>
        <v-card-text v-if="detail">
          <v-alert
              text
              dense
              color="info"
              icon="mdi-alert-octagon-outline"
              border="left"
          >
            <div>{{detail}}</div>
          </v-alert>
        </v-card-text>
        <v-card-text v-else-if="error">
            <v-alert
              text
              dense
              color="error"
              icon="mdi-alert-octagon-outline"
              border="left"
            >
            <div>{{error}}</div>
            </v-alert>
        </v-card-text>
        <v-card-actions class="mr-2 pb-4">
          <v-spacer></v-spacer>
          <v-btn
            color="secondary"
            dark
            class="px-4"
            :to="{ name: 'auth_login'}"
          >
            Sign in?
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
import auth from '../../api/auth';

export default {
  name: 'passwordReset',
  data() {
    return {
      detail: '',
      error: '',
    };
  },
  methods: {
    emailVerify() {
      const payload = this.$route.params;
      auth.verifyAccountEmail(payload).then((response) => {
        this.error = '';
        if ('detail' in response.data) {
          if (response.data.detail === 'ok') {
            this.detail = 'Your e-mail had been verified, you can login now!';
          } else {
            this.detail = response.data.detail;
          }
        } else {
          console.log(response);
          // TODO implement this?
          // this.$cookie.set('token', response.data.key);
          // this.$emit('authenticated', true);
          // this.$router.replace({ name: 'secure' });
        }
      }).catch((r) => {
        if ('detail' in r.response.data) {
          if ('detail' in r.response.data) {
            if (r.response.data.detail === 'Not found.') {
              this.error = 'Your account cannot be verified.';
            } else {
              this.error = r.response.data.detail;
            }
          }
        }
        this.$refs.form.setErrors(r.response.data);
      });
    },
  },
  mounted() {
    this.emailVerify();
  },
};
</script>
