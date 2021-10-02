<template>
  <v-app>
    <core-toolbar/>
    <v-main>
      <router-view></router-view>
    </v-main>
  <core-footer />
  </v-app>
</template>

<script>
export default {
  name: 'PublicView',
};
</script>
