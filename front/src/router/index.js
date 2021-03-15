import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '../store';
import About from '../views/About';
import Home from '../views/Home';
import Lost from '../views/Lost';

// const requireAuthenticated = (to, from, next) => {
//   store.dispatch('auth/initialize')
//     .then(() => {
//       if (!store.getters['auth/isAuthenticated']) {
//         next('/login');
//       } else {
//         next();
//       }
//     });
// };

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


Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/home',
    component: Home,
    name: 'home',
    // beforeEnter: requireAuthenticated,
  },
  {
    path: '/about',
    component: About,
    name: 'about',
    // beforeEnter: requireAuthenticated,
  },
  {
    path: '/auth/signup',
    name: 'auth_signup',
    component: () => import('../views/auth/Signup.vue'),
    beforeEnter: requireUnauthenticated,
  },
  {
    path: '/auth/login',
    name: 'auth_login',
    component: () => import('../views/auth/Login.vue'),
    beforeEnter: requireUnauthenticated,
  },
  {
    path: '/auth/logout',
    name: 'auth_logout',
    beforeEnter: redirectLogout,
  },
  {
    path: '/email-verify/:key',
    name: 'auth_email_verify',
    component: () => import('../views/auth/EmailVerify.vue'),
  },
  {
    path: '/password-forgot',
    name: 'auth_password_forgot',
    component: () => import('../views/auth/PasswordForgot.vue'),
  },
  {
    path: '/password-reset/:uid/:token',
    name: 'auth_password_reset',
    component: () => import('../views/auth/PasswordReset.vue'),
  },
  {
    path: '*',
    component: Lost,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;

// new Router({
//     mode: 'hash', // https://router.vuejs.org/api/#mode
//     routes: [
//         {
//             path: '/',
//             name: 'Home',
//             component: MyComponent,
//             beforeEnter: (to, from, next) => {
//                 if(!isAuthenticated()) {
//                     return next({name: 'login'});
//                 }
//                 return next();
//             },
//         },
//         {
//             path: '/login',
//             name: 'Login',
//             component: LoginComponent
//         }
//     ]
// });
