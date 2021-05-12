<template>
  <v-app>
    <v-app-bar app flat >
      <v-container class="py-0 fill-height">
        <v-avatar  class="mr-10"  color="grey darken-1" size="32"></v-avatar>
        <v-btn :to="{ name: 'home'}" class="mr-2" text>docs</v-btn>
        <v-btn :to="{ name: 'about'}" text>about</v-btn>
        <v-spacer></v-spacer>
        <v-btn :to="{ name: 'auth_signup'}" class="mr-2" text>sign up</v-btn>
        <v-btn :to="{ name: 'auth_login'}" text>login</v-btn>
      </v-container>
    </v-app-bar>
    <v-main>
      <router-view></router-view>
    </v-main>
  <v-footer absolute>
    <v-col class="text-center" cols="12">
      {{ new Date().getFullYear() }} — <strong>BounCA</strong>
    </v-col>
  </v-footer>
  </v-app>
</template>

<script>
export default {
  name: 'PublicView',
};
</script>
