<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
  height?: string
}

withDefaults(defineProps<Props>(), {
  height: '300px',
})
</script>

<template>
  <div class="chart-card">
    <div class="chart-card-header">
      <h3 class="chart-card-title">{{ title }}</h3>
      <p v-if="subtitle" class="chart-card-subtitle">{{ subtitle }}</p>
      <div class="chart-card-actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="chart-card-body" :style="{ height }">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.chart-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.chart-card-header {
  display: flex;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
}

.chart-card-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  flex: 1;
}

.chart-card-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  margin-left: var(--space-3);
}

.chart-card-actions {
  display: flex;
  gap: var(--space-2);
}

.chart-card-body {
  padding: var(--space-4) var(--space-5);
}
</style>
