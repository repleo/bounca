export default [
  {
    path: '/dashboard',
    redirect: '/dashboard/root',
    component: () => import('@/views/Dashboard.vue'),
    children: [
      {
        path: 'root',
        name: 'Root',
        meta: {
          requiresAuth: true,
          displayName: 'Root',
        },
        component: () => import('@/components/dashboard/Dashboard'),
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
