import Vue from 'vue';
import Vuex from 'vuex';
import createLogger from 'vuex/dist/logger';

import auth from './auth';
import dashboard from './dashboard';

// import password from './password';
// import signup from './signup';

const debug = true; // TODO process.env.NODE_ENV !== 'production';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    auth: auth,
    dashboard: dashboard,
    // TODO can it be removed? not used?
    // password,
    // signup,
  },
  strict: debug,
  plugins: debug ? [createLogger()] : [],
});
