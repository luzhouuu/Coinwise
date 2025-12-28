/**
 * Vue Router configuration.
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
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
    },
  },
  {
    path: '/spending-plan',
    name: 'SpendingPlan',
    component: () => import('@/views/SpendingPlanView.vue'),
    meta: {
      title: '消费计划',
      icon: 'budget',
    },
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/views/TransactionsView.vue'),
    meta: {
      title: '交易记录',
      icon: 'list',
    },
  },
  {
    path: '/sync',
    name: 'Sync',
    component: () => import('@/views/SyncView.vue'),
    meta: {
      title: '账单同步',
      icon: 'refresh',
    },
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/ConfigView.vue'),
    meta: {
      title: '设置',
      icon: 'cog',
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Update document title
router.beforeEach((to) => {
  const title = to.meta.title as string;
  document.title = title ? `${title} - 家庭账单` : '家庭账单';
});

export default router;
