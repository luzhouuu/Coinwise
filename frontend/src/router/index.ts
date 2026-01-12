/**
 * Vue Router configuration.
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: {
      title: '概览',
      icon: 'chart-pie',
      requiresAuth: true,
    },
  },
  {
    path: '/spending-plan',
    name: 'SpendingPlan',
    component: () => import('@/views/SpendingPlanView.vue'),
    meta: {
      title: '消费计划',
      icon: 'budget',
      requiresAuth: true,
    },
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/views/TransactionsView.vue'),
    meta: {
      title: '交易记录',
      icon: 'list',
      requiresAuth: true,
    },
  },
  {
    path: '/sync',
    name: 'Sync',
    component: () => import('@/views/SyncView.vue'),
    meta: {
      title: '账单同步',
      icon: 'refresh',
      requiresAuth: true,
    },
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/ConfigView.vue'),
    meta: {
      title: '设置',
      icon: 'cog',
      requiresAuth: true,
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();

  // Update document title
  const title = to.meta.title as string;
  document.title = title ? `${title} - CoinWise` : 'CoinWise';

  // Check if route requires auth
  if (to.meta.requiresAuth !== false) {
    const isAuthenticated = await authStore.checkAuth();
    if (!isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
      return;
    }
  }

  // Redirect to dashboard if already authenticated and going to login
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' });
    return;
  }

  next();
});

export default router;
