import Vue from 'vue';
import Vuex from 'vuex';
import createLogger from 'vuex/dist/logger';

import auth from './auth';
import dashboard from './dashboard';
import version from './version';

const debug = process.env.NODE_ENV !== 'production';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    auth: auth,
    dashboard: dashboard,
    version: version,
  },
  strict: debug,
  plugins: debug ? [createLogger()] : [],
});
