import store from '../store';

const redirectLogout = (to, from, next) => {
  store.dispatch('auth/logout')
    .then(() => next('/'));
};

const redirectLoggedIn = (to, from, next) => {
  if (store.getters['auth/isLoggedIn']) {
    next('/dashboard');
  } else {
    next();
  }
};

export default [
  {
    path: '/auth',
    meta: {
      name: '',
      requiresAuth: false,
    },
    component: () => import(/* webpackChunkName: 'routes' */ '../views/Public.vue'),
    children: [{
      path: '',
      component: () => import('../views/Auth.vue'),
      children: [
        {
          path: '',
          redirect: '/auth/login',
          beforeEnter: redirectLoggedIn,
        },
        {
          path: 'signup',
          name: 'auth_signup',
          component: () => import('../components/auth/Signup.vue'),
          beforeEnter: redirectLoggedIn,
        },
        {
          path: '/auth/logout',
          name: 'auth_logout',
          beforeEnter: redirectLogout,
        },
        {
          path: 'login',
          name: 'auth_login',
          component: () => import('../components/auth/Login.vue'),
          beforeEnter: redirectLoggedIn,
        },
        {
          path: 'account-confirm-email/:key',
          name: 'auth_email_verify',
          component: () => import('../components/auth/EmailVerify.vue'),
        },
        {
          path: 'password-forgot',
          name: 'auth_password_forgot',
          component: () => import('../components/auth/PasswordForgot.vue'),
          beforeEnter: redirectLoggedIn,
        },
        {
          path: 'password-reset/confirm/:uid/:token',
          name: 'auth_password_reset',
          component: () => import('../components/auth/PasswordReset.vue'),
          beforeEnter: redirectLoggedIn,
        },
      ],
    }],
  },
];
