<script setup lang="ts">
/**
 * App header component with title and actions.
 */
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useI18nStore } from '@/stores/i18n';
import LanguageSwitcher from './LanguageSwitcher.vue';

defineProps<{
  sidebarOpen?: boolean;
}>();

const emit = defineEmits<{
  (e: 'toggle-sidebar'): void;
}>();

const route = useRoute();
const i18n = useI18nStore();

const pageTitle = computed(() => route.meta.title as string || '家庭账单');

onMounted(() => {
  i18n.init();
});
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <button
        class="menu-button"
        aria-label="Toggle menu"
        @click="emit('toggle-sidebar')"
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M3 5h14M3 10h14M3 15h14" />
        </svg>
      </button>
      <h1 class="page-title">{{ pageTitle }}</h1>
    </div>
    <div class="header-right">
      <LanguageSwitcher />
      <span class="app-name">Family Spending</span>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  height: var(--header-height);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.menu-button {
  display: none;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.menu-button:hover {
  background: var(--color-background);
  color: var(--color-text-primary);
}

.page-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.app-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

@media (max-width: 768px) {
  .menu-button {
    display: flex;
  }

  .page-title {
    font-size: var(--font-size-lg);
  }
}
</style>
