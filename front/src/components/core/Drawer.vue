<template>
  <v-navigation-drawer
    id="app-drawer"
    clipped
    permanent
    app
    overflow
  >

        <v-list-item>
        <!-- layout, empty space -->
        </v-list-item>
        <v-list-item
          v-for="(link, i) in links"
          :key="i"
          :to="link.to"
          :disabled="!link.active"
          class="v-list-item"
        >
          <v-list-item-action >
            <v-icon>{{ link.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-title>
            {{link.text}}
            <v-list-item-subtitle>
              {{link.subtext}}
            </v-list-item-subtitle>
          </v-list-item-title>

        </v-list-item>
  </v-navigation-drawer>
</template>

<script>
import {
  mapState,
} from 'vuex';

export default {
  data: () => ({
    links: [
      {
        to: '/dashboard/overview',
        icon: 'mdi-home',
        text: 'Overview',
        subtext: '',
        active: true,
      },
      {
        to: '/dashboard/root',
        icon: 'mdi-application-cog',
        text: 'Root Certificates',
        subtext: '',
        active: true,
      },
      {
        to: '/dashboard/intermediate/55',
        icon: 'mdi-application',
        text: 'Intermediate Certificates',
        subtext: '',
        active: false,
      },
      {
        to: '/dashboard/certificate/56',
        icon: 'mdi-certificate',
        text: 'Certificates',
        subtext: '',
        active: false,
      },
    ],
  }),
  computed: {
    ...mapState('dashboard', ['navigation']),
  },
  methods: {
    setRoot() {
      this.links[2].active = this.navigation.root.active;
      this.links[1].subtext = this.navigation.root.name;
      this.links[2].link = `/dashboard/intermediate/${this.navigation.root.id}`;
    },
    setIntermediate() {
      this.links[3].active = this.navigation.intermediate.active;
      this.links[2].subtext = this.navigation.intermediate.name;
      this.links[3].link = `/dashboard/certificate/${this.navigation.intermediate.id}`;
    },
  },
  watch: {
  },
  mounted() {
    this.setRoot();
    this.setIntermediate();
  },
  created() {
    // eslint-disable-next-line no-unused-vars
    this.unsubscribe = this.$store.subscribe((mutation, state) => {
      if (mutation.type === 'dashboard/setRoot') {
        this.setRoot();
      }
      if (mutation.type === 'dashboard/setIntermediate') {
        this.setIntermediate();
      }
    });
  },
  beforeDestroy() {
    this.unsubscribe();
  },
};
</script>
