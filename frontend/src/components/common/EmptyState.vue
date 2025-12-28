<script setup lang="ts">
/**
 * Empty state component for showing when no data is available.
 */
defineProps<{
  title: string;
  description?: string;
  icon?: 'folder' | 'search' | 'chart';
}>();
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">
      <!-- Folder icon -->
      <svg v-if="icon === 'folder'" width="48" height="48" viewBox="0 0 48 48" fill="none">
        <path
          d="M6 14c0-2.21 1.79-4 4-4h8l4 4h16c2.21 0 4 1.79 4 4v18c0 2.21-1.79 4-4 4H10c-2.21 0-4-1.79-4-4V14z"
          stroke="currentColor"
          stroke-width="2"
          fill="none"
        />
      </svg>
      <!-- Search icon -->
      <svg v-else-if="icon === 'search'" width="48" height="48" viewBox="0 0 48 48" fill="none">
        <circle cx="20" cy="20" r="12" stroke="currentColor" stroke-width="2" fill="none" />
        <path d="M30 30l10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </svg>
      <!-- Chart icon -->
      <svg v-else width="48" height="48" viewBox="0 0 48 48" fill="none">
        <rect x="6" y="24" width="8" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none" />
        <rect x="20" y="12" width="8" height="30" rx="2" stroke="currentColor" stroke-width="2" fill="none" />
        <rect x="34" y="18" width="8" height="24" rx="2" stroke="currentColor" stroke-width="2" fill="none" />
      </svg>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p v-if="description" class="empty-description">{{ description }}</p>
    <slot />
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12) var(--space-6);
  text-align: center;
}

.empty-icon {
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-4);
}

.empty-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.empty-description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  max-width: 320px;
  margin-bottom: var(--space-4);
}
</style>
