import store from '../store';

export default [
  {
    path: '*',
    meta: {
      name: '',
      requiresAuth: true,
    },
    redirect: {
      path: '/dashboard',
    },
  },
  {
    path: '/',
    meta: {
      name: '',
      requiresAuth: false,
    },
    component: () => import('../views/Public.vue'),
    // redirect if already signed in
    beforeEnter: (to, from, next) => {
      if (store.getters['auth/isLoggedIn']) {
        next('/dashboard');
      } else {
        next();
      }
    },
    children: [
      {
        path: '',
        redirect: '/auth/login',
      },
    ],
  },
];
