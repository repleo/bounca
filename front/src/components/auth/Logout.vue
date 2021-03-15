<template>
  <v-btn
    dark
    color="secondary"
    class="px-4"
    @click="logout"
  >
    Logout
  </v-btn>
</template>

<script>
import auth from '../../api/auth';

export default {
  name: 'Logout',
  data() {
    return {
    };
  },
  methods: {
    logout() {
      auth.logout().then((response) => {
        console.log(response);
        this.$cookie.set('token', '');
        // this.$emit('authenticated', true);
        // this.$router.replace({ name: 'secure' });
      }).catch((r) => {
        console.log(r);
      });
    }
  },
};
</script>

