<template>
    <v-app-bar id="core-toolbar" flat clipped-left app>
      <v-list-item>
          <router-link to="/">
            <v-list-item-avatar
              size="65"
            >
              <v-img
                :src="require('../../assets/img/BounCA-logo.png')"
                contain
              />
          </v-list-item-avatar>
          </router-link>

          <v-list-item-title>
            <div class="title">
            BounCA - Key Management
            </div>
            <div class="font-weight-thin">
              V{{ appVersion }}
            </div>
          </v-list-item-title>
      </v-list-item>
      <v-spacer/>
      <template v-if="loggedIn">
        <v-btn :to="{ name: 'user_profile'}" icon><v-icon color>mdi-account</v-icon></v-btn>
        <v-btn :to="{ name: 'auth_logout'}" icon><v-icon>mdi-power</v-icon></v-btn>
      </template>
      <template v-else>
        <v-btn :to="{ name: 'auth_signup'}" class="mr-2" text>sign up</v-btn>
        <v-btn :to="{ name: 'auth_login'}" text>login</v-btn>
      </template>
    </v-app-bar>
</template>

<script>
import store from '../../store';

export default {
  data: () => ({
    loggedIn: false,
  }),
  created() {
    // eslint-disable-next-line no-unused-vars
    this.unsubscribe = this.$store.subscribe((mutation, state) => {
      if (mutation.type.startsWith('auth/')) {
        this.loggedIn = store.getters['auth/isLoggedIn'];
      }
    });
  },
  beforeDestroy() {
    this.unsubscribe();
  },
  mounted() {
    this.loggedIn = store.getters['auth/isLoggedIn'];
  },
  computed: {
    appVersion() {
      return store.getters['version/appVersion'];
    },
  },
};
</script>
