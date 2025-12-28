<script setup lang="ts">
/**
 * Loading spinner component.
 */
defineProps<{
  size?: 'sm' | 'md' | 'lg';
}>();
</script>

<template>
  <div class="spinner-container">
    <div class="spinner" :class="size || 'md'" />
  </div>
</template>

<style scoped>
.spinner-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}

.spinner {
  border-radius: 50%;
  border-style: solid;
  border-color: var(--color-border);
  border-top-color: var(--color-primary);
  animation: spin 0.8s linear infinite;
}

.spinner.sm {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

.spinner.md {
  width: 24px;
  height: 24px;
  border-width: 3px;
}

.spinner.lg {
  width: 40px;
  height: 40px;
  border-width: 4px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
