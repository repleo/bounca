import Vue from 'vue';
import Router from 'vue-router';
import Meta from 'vue-meta';
import axios from 'axios';

import store from '../store';

// Routes
import home from './home';
import auth from './auth';
import dashboard from './dashboard';

Vue.use(Router);

// Create a new router
const router = new Router({
  base: '',
  mode: 'history',
  routes: home.concat(auth, dashboard),

  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    if (to.hash) {
      return { selector: to.hash };
    }
    return { x: 0, y: 0 };
  },
});

router.beforeEach((to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (store.getters['auth/isLoggedIn']) {
      next();
      return;
    }
    next('/');
  } else {
    next();
  }
});

Vue.use(Meta);

export default router;

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response.status === 403 || error.response.status === 401) {
      store.dispatch('auth/logout').then(() => router.push('/'));
    }
    return Promise.reject(error);
  },
);
