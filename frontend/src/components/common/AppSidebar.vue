<script setup lang="ts">
/**
 * App sidebar navigation component.
 */
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18nStore } from '@/stores/i18n';

defineProps<{
  open?: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const route = useRoute();
const router = useRouter();
const i18n = useI18nStore();

const navItems = computed(() => [
  { path: '/dashboard', name: i18n.t('nav.dashboard'), icon: 'chart' },
  { path: '/spending-plan', name: i18n.t('nav.spending_plan'), icon: 'budget' },
  { path: '/transactions', name: i18n.t('nav.transactions'), icon: 'list' },
  { path: '/sync', name: i18n.t('nav.sync'), icon: 'sync' },
  { path: '/config', name: i18n.t('nav.config'), icon: 'cog' },
]);

function isActive(path: string): boolean {
  return route.path === path;
}

function navigateTo(path: string): void {
  router.push(path);
  emit('close');
}
</script>

<template>
  <aside class="sidebar" :class="{ open }">
    <div class="sidebar-header">
      <div class="logo">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="16" r="14" fill="var(--color-primary)" />
          <circle cx="16" cy="16" r="10" stroke="white" stroke-width="2" fill="none" />
          <text x="16" y="21" text-anchor="middle" fill="white" font-size="12" font-weight="bold">$</text>
        </svg>
        <span class="logo-text">CoinWise</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <button
        v-for="item in navItems"
        :key="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
        @click="navigateTo(item.path)"
      >
        <span class="nav-icon">
          <!-- Chart icon -->
          <svg v-if="item.icon === 'chart'" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M2 10a8 8 0 1116 0 8 8 0 01-16 0zm8-6a6 6 0 100 12 6 6 0 000-12z" />
            <path d="M10 4v6l4 2" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" />
          </svg>
          <!-- List icon -->
          <svg v-else-if="item.icon === 'list'" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M3 4h14a1 1 0 110 2H3a1 1 0 110-2zm0 5h14a1 1 0 110 2H3a1 1 0 110-2zm0 5h14a1 1 0 110 2H3a1 1 0 110-2z" />
          </svg>
          <!-- Sync icon -->
          <svg v-else-if="item.icon === 'sync'" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" />
          </svg>
          <!-- Cog icon -->
          <svg v-else-if="item.icon === 'cog'" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
          </svg>
          <!-- Budget icon -->
          <svg v-else-if="item.icon === 'budget'" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z" />
            <path fill-rule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clip-rule="evenodd" />
          </svg>
        </span>
        <span class="nav-text">{{ item.name }}</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <span class="version">v1.0.0</span>
    </div>
  </aside>

  <!-- Overlay for mobile -->
  <div v-if="open" class="sidebar-overlay" @click="emit('close')" />
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: var(--z-sticky);
}

.sidebar-header {
  padding: var(--space-5) var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.logo-text {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
  text-align: left;
  width: 100%;
}

.nav-item:hover {
  background: var(--color-background);
  color: var(--color-text-primary);
}

.nav-item.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
}

.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid var(--color-border);
}

.version {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.sidebar-overlay {
  display: none;
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform var(--transition-base);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.3);
    z-index: calc(var(--z-sticky) - 1);
  }
}
</style>
