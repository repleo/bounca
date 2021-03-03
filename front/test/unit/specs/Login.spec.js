import Vue from 'vue';
import Router from 'vue-router';

import Login from '@/views/Login';

describe('Login.vue', () => {
  it('should render expected contents', () => {
    const Constructor = Vue.extend(Login);
    const router = new Router();
    const vm = new Constructor({ router }).$mount();
    expect(vm.$el.querySelector('#login-view h1').textContent)
      .to.equal('Login');
  });
});
