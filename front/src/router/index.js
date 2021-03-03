import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '../store';
import About from '../views/About';
import Home from '../views/Home';
import Lost from '../views/Lost';

const requireAuthenticated = (to, from, next) => {
  store.dispatch('auth/initialize')
    .then(() => {
      if (!store.getters['auth/isAuthenticated']) {
        next('/login');
      } else {
        next();
      }
    });
};

const requireUnauthenticated = (to, from, next) => {
  store.dispatch('auth/initialize')
    .then(() => {
      if (store.getters['auth/isAuthenticated']) {
        next('/home');
      } else {
        next();
      }
    });
};

const redirectLogout = (to, from, next) => {
  store.dispatch('auth/logout')
    .then(() => next('/login'));
};


Vue.use(VueRouter)

  const routes = [
  {
      path: '/',
      redirect: '/home',
  },
  {
      path: '/home',
      component: Home,
      beforeEnter: requireAuthenticated,
  },
  {
      path: '/about',
      component: About,
      beforeEnter: requireAuthenticated,
  },
  {
    path: '/signup',
    name: 'signup',
    component: () => import('../views/auth/Signup.vue'),
    beforeEnter: requireUnauthenticated,
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/auth/Login.vue'),
    beforeEnter: requireUnauthenticated,
  },
  {
    path: '/logout',
    beforeEnter: redirectLogout,
  },
  {
    path: '/email-verify/:key',
    name: 'email-verify',
    component: () => import('../views/auth/EmailVerify.vue')
  },
  {
    path: '/password-forgot',
    name: 'password-forgot',
    component: () => import('../views/auth/PasswordForgot.vue')
  },
  {
    path: '/password-reset/:uid/:token',
    name: 'password-reset',
    component: () => import('../views/auth/PasswordReset.vue')
  },
  {
    path: '/password-reset-confirm',
    name: 'password-reset-confirm',
    component: () => import('../views/auth/PasswordResetConfirm.vue')
  },
  {
    path: '*',
    component: Lost,
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router

