<template>
  <v-app>
    <core-drawer/>
    <core-toolbar/>
    <v-main>
      <v-fade-transition mode="out-in">
        <router-view />
      </v-fade-transition>
    </v-main>
    <core-footer />
  </v-app>
</template>

<script>
export default {
  name: 'DashboardView',
  metaInfo() {
    return {
      title: 'BounCA Dashboard',
    };
  },
};
</script>

<style>
</style>
