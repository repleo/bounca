<template>
  <v-footer
    dark
    padless
    app
  >
    <v-card
      class="flex"
      flat
      tile
    >
      <v-card-title class="teal">
        <strong class="subheading">More info and get connected:</strong>
        <v-spacer></v-spacer>
        <v-btn
          v-for="link in links"
          :href="link.href"
          :key="link.name"
          class="mx-3"
          plain
          dark
          target="_blank"
        >
          {{ link.name }}
        </v-btn>
      </v-card-title>

      <v-card-text class="py-2 white--text text-center">
        &copy; 2016 - {{ (new Date()).getFullYear() }} —
        <a
          href="https://www.bounca.org"
          target="_blank"
          class="white--text font-weight-black"
        >
          BounCA.org</a>, made by
        <a
          href="https://www.repleo.nl"
          class="white--text font-weight-black"
          target="_blank">Repleo.nl</a>, Amsterdam, The Netherlands
      </v-card-text>
    </v-card>
  </v-footer>
</template>

<script>
export default {
  name: 'CoreFooter',
  data: () => ({
    links: [
      { name: 'Feature requests', href: 'https://gitlab.com/bounca/bounca/-/issues' },

      { name: 'API', href: '/api' },
      { name: 'Documentation', href: 'https://www.bounca.org/' },
      { name: 'GitLab', href: 'https://gitlab.com/bounca/bounca' },
      { name: 'Twitter', href: 'https://twitter.com/gobounca' },
    ],
  }),
};
</script>

<style>
a{
 text-decoration: none;
}
</style>
