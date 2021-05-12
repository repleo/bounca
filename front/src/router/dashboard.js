export default [
  {
    path: '/dashboard',
    meta: {
      displayName: 'Dashboard',
      requiresAuth: true,
    },
    component: () => import('@/views/Dashboard.vue'),
    children: [
      {
        path: '',
        name: 'Dashboard',
        meta: {
          requiresAuth: true,
          displayName: 'Dashboard',
        },
        component: () => import('@/components/dashboard/Dashboard.vue'),
      },
      {
        path: 'user/profile',
        name: 'user_profile',
        meta: {
          requiresAuth: true,
          displayName: 'Profile',
        },
        component: () => import('@/components/dashboard/user/UserProfile.vue'),
      },
      {
        path: 'user/settings',
        name: 'user_settings',
        meta: {
          requiresAuth: true,
          displayName: 'Settings',
        },
        component: () => import('@/components/dashboard/user/UserSettings.vue'),
      },
    ],
  },
];
