import Vue from 'vue'
import { ValidationObserver, ValidationProvider, extend, localize } from 'vee-validate';
import en from 'vee-validate/dist/locale/en.json';
import * as rules from 'vee-validate/dist/rules';
import App from './App.vue'
import router from './router'
var VueCookie = require('vue-cookie')

Vue.use(VueCookie)

// install rules and localization
Object.keys(rules).forEach(rule => {
  extend(rule, rules[rule]);
});

localize('en', en);

Vue.component('ValidationObserver', ValidationObserver);
Vue.component('ValidationProvider', ValidationProvider);

import 'bootstrap/dist/css/bootstrap.min.css'
import '@/assets/css/main.css'
import '@/assets/css/bounca.css'

Vue.config.productionTip = false //TODO what is this

// var instance = axios.create({
//     xsrfCookieName: 'csrftoken',
//     xsrfHeaderName: "X-CSRFTOKEN",
// });

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

