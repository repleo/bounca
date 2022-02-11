import Vue from 'vue';
import Axios from 'axios';
import {
  ValidationObserver,
  ValidationProvider,
  localize,
  extend,
  setInteractionMode,
} from 'vee-validate';
import en from 'vee-validate/dist/locale/en.json';
import * as rules from 'vee-validate/dist/rules';

import App from './App.vue';
import router from './router';
import store from './store';

// Components
import './components/index';

import vuetify from './plugins/vuetify';

/* vee-validate config */
setInteractionMode('eager');
Vue.component('extendValidation', extend);
Vue.component('ValidationObserver', ValidationObserver);
Vue.component('ValidationProvider', ValidationProvider);

// install rules and localization
Object.keys(rules).forEach((rule) => {
  extend(rule, rules[rule]);
});
extend('url', {
  validate(value) {
    const pattern = new RegExp('^(https?:\\/\\/)?' // protocol
      + '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' // domain name
      + '((\\d{1,3}\\.){3}\\d{1,3}))' // OR ip (v4) address
      + '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' // port and path
      + '(\\?[;&a-z\\d%_.~+=-]*)?' // query string
      + '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator
    return pattern.test(value);
  },
  message: 'Please enter a valid URL',
});
localize('en', en);
/* vee-validate config */

Vue.config.productionTip = process.env.NODE_ENV === 'production';

Vue.prototype.$http = Axios;
const key = localStorage.getItem('user-key');
if (key) {
  Vue.prototype.$http.defaults.headers.common.Authorization = key;
}

new Vue({
  router,
  store,
  vuetify,
  render: (h) => h(App),
}).$mount('#app');
