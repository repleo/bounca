import Vue from 'vue';
import Router from 'vue-router';
import Meta from 'vue-meta';
// import NProgress from "nprogress";
import store from '@/store';

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
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (store.getters['auth/isLoggedIn']) {
      next();
      return;
    }
    next('/');
  } else {
    next();
  }
});

// router.beforeResolve((to, from, next) => {
//   if (to.path) {
//     NProgress.start();
//   }
//   next();
// });
//
// router.afterEach(() => {
//   NProgress.done();
// });

Vue.use(Meta);

export default router;
