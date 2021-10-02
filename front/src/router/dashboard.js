export default [
  {
    path: '/dashboard',
    redirect: '/dashboard/overview',
    component: () => import('@/views/Dashboard.vue'),
    children: [
      {
        path: 'overview',
        name: 'Overview',
        meta: {
          requiresAuth: true,
          displayName: 'Overview',
        },
        component: () => import('@/components/dashboard/Overview.vue'),
      },
      {
        path: 'root',
        name: 'Root',
        meta: {
          requiresAuth: true,
          displayName: 'Root',
        },
        component: () => import('@/components/dashboard/Root.vue'),
      },
      {
        path: 'intermediate/:id',
        name: 'Intermediate',
        meta: {
          requiresAuth: true,
          displayName: 'Intermediate',
        },
        component: () => import('@/components/dashboard/Intermediate'),
      },
      {
        path: 'certificate/:id',
        name: 'Certificate',
        meta: {
          requiresAuth: true,
          displayName: 'Certificate',
        },
        component: () => import('@/components/dashboard/Certificate.vue'),
      },
      {
        path: 'user/profile',
        name: 'user_profile',
        meta: {
          requiresAuth: true,
          displayName: 'Profile',
        },
        component: () => import('@/components/dashboard/user/UserProfile'),
      },
      {
        path: 'user/settings',
        name: 'user_settings',
        meta: {
          requiresAuth: true,
          displayName: 'Settings',
        },
        component: () => import('@/components/dashboard/user/UserSettings'),
      },
    ],
  },
];
