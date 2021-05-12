<template>
    <v-app-bar id="core-toolbar" flat clipped-left app>
      <v-list-item>
          <v-list-item-avatar
            color="grey"
          >
            <v-img
              :src="logo"
              contain
            />
          </v-list-item-avatar>
          <v-list-item-title class="title">
            BounCA
          </v-list-item-title>
      </v-list-item>
      <v-spacer/>
      <v-btn :to="{ name: 'user_profile'}" icon><v-icon color>mdi-account</v-icon></v-btn>
      <v-btn :to="{ name: 'user_settings'}" icon><v-icon color>mdi-cog</v-icon></v-btn>
      <v-btn :to="{ name: 'auth_logout'}" icon><v-icon>mdi-power</v-icon></v-btn>
    </v-app-bar>
</template>

<!--<template>-->
<!--  <v-card class="overflow-hidden">-->
<!--      <v-app-bar-->
<!--      color="deep-purple accent-4"-->
<!--      dense-->
<!--      dark-->
<!--    >-->
<!--      <v-app-bar-nav-icon></v-app-bar-nav-icon>-->

<!--      <v-toolbar-title>Page title</v-toolbar-title>-->

<!--      <v-spacer></v-spacer>-->

<!--      <v-btn icon>-->
<!--        <v-icon>mdi-heart</v-icon>-->
<!--      </v-btn>-->

<!--      <v-btn icon>-->
<!--        <v-icon>mdi-magnify</v-icon>-->
<!--      </v-btn>-->

<!--      <v-menu-->
<!--        left-->
<!--        bottom-->
<!--      >-->
<!--        <template v-slot:activator="{ on, attrs }">-->
<!--          <v-btn-->
<!--            icon-->
<!--            v-bind="attrs"-->
<!--            v-on="on"-->
<!--          >-->
<!--            <v-icon>mdi-dots-vertical</v-icon>-->
<!--          </v-btn>-->
<!--        </template>-->

<!--        <v-list>-->
<!--          <v-list-item-->
<!--            v-for="n in 5"-->
<!--            :key="n"-->
<!--            @click="() => {}"-->
<!--          >-->
<!--            <v-list-item-title>Option {{ n }}</v-list-item-title>-->
<!--          </v-list-item>-->
<!--        </v-list>-->
<!--      </v-menu>-->
<!--    </v-app-bar>-->
<!--  </v-card>-->
<!--</template>-->


<script>

export default {
  data: () => ({
    title: '',
    responsive: false,
    responsiveInput: false,
  }),

  watch: {
    // TODO not set when just refreshed
    $route(val) {
      this.title = val.meta.displayName;
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
    onResponsiveInverted() {
      if (window.innerWidth < 991) {
        this.responsive = true;
        this.responsiveInput = false;
      } else {
        this.responsive = false;
        this.responsiveInput = true;
      }
    },
  },
};
</script>
