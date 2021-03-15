<template>
  <v-app>
<!--    &lt;!&ndash; Start of Navigation &ndash;&gt;-->
<!--    <nav>-->
<!--      &lt;!&ndash; Start of app toolbar &ndash;&gt;-->
<!--      <v-toolbar app>-->
<!--        <v-app-bar-nav-icon-->
<!--          @click.stop="drawer = !drawer"-->
<!--          class="hidden-md-and-up"-->
<!--        ><v-icon>more_vert</v-icon></v-app-bar-nav-icon>-->
<!--        <v-toolbar-title class="headline text-uppercase"-->
<!--          >Vuetify Demo</v-toolbar-title-->
<!--        >-->
<!--        <v-spacer></v-spacer>-->
<!--        <v-toolbar-items class="hidden-sm-and-down">-->
<!--          <v-btn flat :to="{ name: 'home'}" exact>Home</v-btn>-->
<!--          <v-btn flat :to="{ name: 'about'}">About</v-btn>-->
<!--        </v-toolbar-items>-->
<!--      </v-toolbar>-->
<!--      &lt;!&ndash; End of app toolbar &ndash;&gt;-->

<!--      &lt;!&ndash; Start of mobile side menu &ndash;&gt;-->
<!--      <v-navigation-drawer app v-model="drawer" right>-->
<!--        &lt;!&ndash; Menu title &ndash;&gt;-->
<!--        <v-toolbar flat>-->
<!--          <v-list>-->
<!--            <v-list-tile>-->
<!--              <v-list-tile-title class="title">Menu</v-list-tile-title>-->
<!--            </v-list-tile>-->
<!--          </v-list>-->
<!--        </v-toolbar>-->
<!--        <v-divider></v-divider>-->
<!--        &lt;!&ndash; Menu Links &ndash;&gt;-->
<!--        <v-list>-->
<!--          <v-list-tile :to="{ name: 'home'}" exact>-->
<!--            <v-list-tile-action>-->
<!--              <v-icon>home</v-icon>-->
<!--            </v-list-tile-action>-->
<!--            <v-list-tile-content>Home</v-list-tile-content>-->
<!--          </v-list-tile>-->
<!--          <v-list-tile :to="{ name: 'about'}">-->
<!--            <v-list-tile-action>-->
<!--              <v-icon>description</v-icon>-->
<!--            </v-list-tile-action>-->
<!--            <v-list-tile-content>About</v-list-tile-content>-->
<!--          </v-list-tile>-->
<!--        </v-list>-->
<!--      </v-navigation-drawer>-->
<!--      &lt;!&ndash; End of mobile side menu &ndash;&gt;-->
<!--    </nav>-->
<!--    &lt;!&ndash; End of Navigation &ndash;&gt;-->

    <v-app-bar app flat >
      <v-container class="py-0 fill-height">
        <v-avatar  class="mr-10"  color="grey darken-1" size="32"></v-avatar>
        <v-btn :to="{ name: 'home'}" text>docs</v-btn>
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
  name: 'BounCA',
  data: () => ({
    drawer: false,
  }),
};
</script>
