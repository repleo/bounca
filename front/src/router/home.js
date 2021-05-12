import store from '../api/store';

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
    component: () =>
      import(/* webpackChunkName: 'routes' */ '@/views/Public.vue'),
    // redirect if already signed in
    beforeEnter: (to, from, next) => {
      if (store.getters.isLoggedIn) {
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
      {
        path: 'docs',
        name: 'home',
        component: () => import('@/components/public/Docs.vue'),
      },
      {
        path: 'about',
        name: 'about',
        component: () => import('@/components/public/About.vue'),
      },
    ],
  },
];
