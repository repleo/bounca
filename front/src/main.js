import Vue from 'vue';
import Axios from 'axios';
import { ValidationObserver, ValidationProvider, localize, extend, setInteractionMode } from 'vee-validate';
import en from 'vee-validate/dist/locale/en.json';
import * as rules from 'vee-validate/dist/rules';

import App from './App';
import router from './router';
import store from './api/store';

// Components
import './components/index';

// import 'bootstrap/dist/css/bootstrap.min.css';
// import '@/assets/css/main.css';
// import '@/assets/css/bounca.css';
import vuetify from './plugins/vuetify';

// const VueCookie = require('vue-cookie');
//
// Vue.use(VueCookie);

/* vee-validate config */
setInteractionMode('eager');
Vue.component('extend', extend);
Vue.component('ValidationObserver', ValidationObserver);
Vue.component('ValidationProvider', ValidationProvider);

// install rules and localization
Object.keys(rules).forEach((rule) => {
  extend(rule, rules[rule]);
});
localize('en', en);
/* vee-validate config */

// Vue.config.productionTip = false; // TODO what is this

// var instance = axios.create({
//     xsrfCookieName: 'csrftoken',
//     xsrfHeaderName: "X-CSRFTOKEN",
// });

Vue.prototype.$http = Axios;
const key = localStorage.getItem('user-key');
if (key) {
  Vue.prototype.$http.defaults.headers.common.Authorization = key;
}

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App),
}).$mount('#app');
