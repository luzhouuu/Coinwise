<script setup lang="ts">
import { computed } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import type { BudgetSummaryItem } from '@/api/budgets'

interface Props {
  item: BudgetSummaryItem
}

const props = defineProps<Props>()
const emit = defineEmits<{
  edit: [item: BudgetSummaryItem]
  delete: [item: BudgetSummaryItem]
}>()

const i18n = useI18nStore()

const progressWidth = computed(() => {
  return Math.min(props.item.percentage_used, 100)
})

const statusClass = computed(() => {
  if (props.item.percentage_used > 100) return 'over'
  if (props.item.percentage_used > 80) return 'warning'
  return 'normal'
})

const statusText = computed(() => {
  if (props.item.percentage_used > 100) return i18n.t('status.over_budget')
  if (props.item.percentage_used > 80) return i18n.t('status.warning')
  return i18n.t('status.on_track')
})
</script>

<template>
  <div class="budget-goal-card">
    <div class="goal-category">
      <span
        class="category-dot"
        :style="{ backgroundColor: item.category_color || '#8E8E93' }"
      ></span>
      <span class="category-name">{{ item.category_name }}</span>
    </div>

    <div class="goal-amounts">
      <div class="amount-item">
        <span class="amount-label">{{ i18n.t('table.budget') }}</span>
        <span class="amount-value">{{ i18n.formatCurrency(item.budget_amount) }}</span>
      </div>
      <div class="amount-item">
        <span class="amount-label">{{ i18n.t('table.spent') }}</span>
        <span class="amount-value" :class="statusClass">
          {{ i18n.formatCurrency(item.spent_amount) }}
        </span>
      </div>
      <div class="amount-item">
        <span class="amount-label">{{ i18n.t('table.remaining') }}</span>
        <span class="amount-value" :class="{ negative: item.remaining < 0 }">
          {{ i18n.formatCurrency(item.remaining) }}
        </span>
      </div>
    </div>

    <div class="goal-progress">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :class="statusClass"
          :style="{ width: `${progressWidth}%` }"
        ></div>
      </div>
      <div class="progress-info">
        <span class="progress-percent" :class="statusClass">
          {{ item.percentage_used.toFixed(1) }}%
        </span>
        <span class="progress-status" :class="statusClass">{{ statusText }}</span>
      </div>
    </div>

    <div class="goal-actions">
      <button class="action-btn edit-btn" @click="emit('edit', item)" :title="i18n.t('common.edit')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M11.333 2a1.886 1.886 0 012.667 2.667l-8.333 8.333-3.334 1 1-3.333 8.333-8.334-.333-.333z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <button class="action-btn delete-btn" @click="emit('delete', item)" :title="i18n.t('common.delete')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M2 4h12M5.333 4V2.667a1.333 1.333 0 011.334-1.334h2.666a1.333 1.333 0 011.334 1.334V4m2 0v9.333a1.333 1.333 0 01-1.334 1.334H4.667a1.333 1.333 0 01-1.334-1.334V4h9.334z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.budget-goal-card {
  display: grid;
  grid-template-columns: 1fr 2fr 1.5fr auto;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.budget-goal-card:hover {
  border-color: var(--color-primary);
}

@media (max-width: 768px) {
  .budget-goal-card {
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }
}

.goal-category {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.category-dot {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.category-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.goal-amounts {
  display: flex;
  gap: var(--space-6);
}

.amount-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.amount-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.amount-value {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.amount-value.warning {
  color: var(--color-warning);
}

.amount-value.over {
  color: var(--color-error);
}

.amount-value.negative {
  color: var(--color-error);
}

.goal-progress {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.progress-bar {
  height: 8px;
  background: var(--color-border-light);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-base);
}

.progress-fill.normal {
  background: var(--color-success);
}

.progress-fill.warning {
  background: var(--color-warning);
}

.progress-fill.over {
  background: var(--color-error);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-percent {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.progress-percent.normal {
  color: var(--color-success);
}

.progress-percent.warning {
  color: var(--color-warning);
}

.progress-percent.over {
  color: var(--color-error);
}

.progress-status {
  font-size: var(--font-size-xs);
}

.progress-status.normal {
  color: var(--color-success);
}

.progress-status.warning {
  color: var(--color-warning);
}

.progress-status.over {
  color: var(--color-error);
}

.goal-actions {
  display: flex;
  gap: var(--space-2);
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.edit-btn {
  color: var(--color-text-secondary);
}

.edit-btn:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.delete-btn {
  color: var(--color-text-secondary);
}

.delete-btn:hover {
  background: var(--color-error-light);
  color: var(--color-error);
}
</style>
