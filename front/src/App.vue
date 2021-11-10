<style lang="sass">
    @import '../node_modules/typeface-roboto/index.css'
</style>

<template>
  <transition mode="out-in">
    <router-view />
  </transition>
</template>

<script>
export default {
  name: 'BounCA',
  computed: {
    isLoggedIn: function () {
      return this.$store.getters.isLoggedIn;
    },
  },
  // TODO checks to see if token is valid or has expired, if it gets back 401 error log out
  //   created: function () {
  //   this.$http.interceptors.response.use(
  //     (response) => {
  //       return response;
  //     },
  //     (error) => {
  //       if (error.response.status === 401) {
  //         if (this.$store.getters.authorized) {
  //           this.$store.dispatch("refreshtoken");
  //         } else {
  //           return Promise.reject(error);
  //         }
  //       } else {
  //         return Promise.reject(error);
  //       }
  //     }
  //   );
  // },
};
</script>
