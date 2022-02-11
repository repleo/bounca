import 'material-design-icons-iconfont/dist/material-design-icons.css';
import '@mdi/font/css/materialdesignicons.css';
import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';
import colors from 'vuetify/es5/util/colors';

Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    iconFont: 'md',
  },
  theme: {
    themes: {
      light: {
        primary: colors.indigo.base,
        secondary: colors.teal.base,
        accent: colors.red.base,
        error: colors.red.base,
        warning: colors.deepOrange.base,
        info: colors.blueGrey.base,
        success: colors.lightGreen.base,
      },
    },
  },
});
