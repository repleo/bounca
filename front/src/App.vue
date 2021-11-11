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

  // created: function () {
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
