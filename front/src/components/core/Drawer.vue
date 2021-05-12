<template>
  <v-navigation-drawer
    id="app-drawer"
    v-model="inputValue"
    clipped
    permanent
    app
    overflow
  >

        <v-list-item>
          <v-text-field
            class="purple-input search-input"
            label="Search..."
            color="purple"
          />
        </v-list-item>
        <v-list-item
          v-for="(link, i) in links"
          :key="i"
          :to="link.to"
          :active-class="color"
          avatar
          class="v-list-item"
        >
          <v-list-item-action>
            <v-icon>{{ link.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-title
            v-text="link.text"
          />
        </v-list-item>
  </v-navigation-drawer>
</template>

<script>
// Utilities
import {
  mapMutations,
  mapState,
} from 'vuex';

export default {
  data: () => ({
    links: [
      {
        to: '/dashboard',
        icon: 'mdi-view-dashboard',
        text: 'Dashboard',
      },
      {
        to: '/dashboard/root-certficates',
        icon: 'mdi-account',
        text: 'Root Certificates',
      },
      {
        to: '/dashboard/intermediate-certificates',
        icon: 'mdi-clipboard-outline',
        text: 'Intermediate Certificates',
      },
      {
        to: '/dashboard/client-certificates',
        icon: 'mdi-table-edit',
        text: 'Client Certificates',
      },
      {
        to: '/dashboard/server-certificates',
        icon: 'mdi-format-font',
        text: 'Server Certificates',
      },
      {
        to: '/dashboard/personal-certifcates',
        icon: 'mdi-chart-bubble',
        text: 'Personal Certficates',
      },
    ],
    responsive: false,
  }),
  computed: {
    ...mapState('app', ['image', 'color']),
    inputValue: {
      get() {
        return null;
      },
      set(val) {
        this.setDrawer(val);
      },
    },
    items() {
      return this.$t('Layout.View.items');
    },
  },
  mounted() {
    this.onResponsiveInverted();
    window.addEventListener('resize', this.onResponsiveInverted);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResponsiveInverted);
  },
  methods: {
    ...mapMutations('app', ['setDrawer', 'toggleDrawer']),
    onResponsiveInverted() {
      if (window.innerWidth < 991) {
        this.responsive = true;
      } else {
        this.responsive = false;
      }
    },
  },
};
</script>

<style lang="scss">
  #app-drawer {
    .v-list__tile {
      border-radius: 4px;

      &--buy {
        margin-top: auto;
        margin-bottom: 17px;
      }
    }

    .v-image__image--contain {
      top: 9px;
      height: 60%;
    }

    .search-input {
      margin-bottom: 30px !important;
      padding-left: 15px;
      padding-right: 15px;
    }
  }
</style>
