<script setup lang="ts">
import { computed } from 'vue'
import { useBudgetStore } from '@/stores/budgets'
import { useI18nStore } from '@/stores/i18n'

const budgetStore = useBudgetStore()
const i18n = useI18nStore()

const percentageUsed = computed(() => {
  if (!budgetStore.summary || budgetStore.summary.total_budget === 0) return 0
  return Math.round((budgetStore.summary.total_spent / budgetStore.summary.total_budget) * 100)
})

const statusClass = computed(() => {
  if (percentageUsed.value > 100) return 'over'
  if (percentageUsed.value > 80) return 'warning'
  return 'normal'
})
</script>

<template>
  <div class="budget-overview">
    <div class="overview-card">
      <div class="card-icon budget-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z" fill="currentColor"/>
        </svg>
      </div>
      <div class="card-content">
        <span class="card-label">{{ i18n.t('budget.total_budget') }}</span>
        <span class="card-value">{{ i18n.formatCurrency(budgetStore.summary?.total_budget || 0) }}</span>
      </div>
    </div>

    <div class="overview-card">
      <div class="card-icon spent-icon" :class="statusClass">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="currentColor"/>
        </svg>
      </div>
      <div class="card-content">
        <span class="card-label">{{ i18n.t('budget.total_spent') }}</span>
        <span class="card-value" :class="statusClass">
          {{ i18n.formatCurrency(budgetStore.summary?.total_spent || 0) }}
        </span>
        <span class="card-percent" :class="statusClass">{{ percentageUsed }}% {{ i18n.t('budget.of_budget') }}</span>
      </div>
    </div>

    <div class="overview-card">
      <div class="card-icon remaining-icon" :class="{ negative: (budgetStore.summary?.total_remaining || 0) < 0 }">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14h-2V7h2v10zm4 0h-2V9h2v8zm-8 0H6v-6h2v6z" fill="currentColor"/>
        </svg>
      </div>
      <div class="card-content">
        <span class="card-label">{{ i18n.t('budget.remaining') }}</span>
        <span class="card-value" :class="{ negative: (budgetStore.summary?.total_remaining || 0) < 0 }">
          {{ i18n.formatCurrency(budgetStore.summary?.total_remaining || 0) }}
        </span>
      </div>
    </div>

    <div class="overview-card">
      <div class="card-icon categories-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M12 2l-5.5 9h11L12 2zm0 3.84L13.93 9h-3.87L12 5.84zM17.5 13c-2.49 0-4.5 2.01-4.5 4.5s2.01 4.5 4.5 4.5 4.5-2.01 4.5-4.5-2.01-4.5-4.5-4.5zm0 7c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5zM3 21.5h8v-8H3v8zm2-6h4v4H5v-4z" fill="currentColor"/>
        </svg>
      </div>
      <div class="card-content">
        <span class="card-label">{{ i18n.t('budget.categories') }}</span>
        <span class="card-value">{{ budgetStore.summary?.category_count || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.budget-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

@media (max-width: 1024px) {
  .budget-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .budget-overview {
    grid-template-columns: 1fr;
  }
}

.overview-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.budget-icon {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.spent-icon {
  background: var(--color-success-light);
  color: var(--color-success);
}

.spent-icon.warning {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.spent-icon.over {
  background: var(--color-error-light);
  color: var(--color-error);
}

.remaining-icon {
  background: var(--color-info-light);
  color: var(--color-info);
}

.remaining-icon.negative {
  background: var(--color-error-light);
  color: var(--color-error);
}

.categories-icon {
  background: #F3E8FF;
  color: #AF52DE;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.card-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.card-value {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.card-value.warning {
  color: var(--color-warning);
}

.card-value.over {
  color: var(--color-error);
}

.card-value.negative {
  color: var(--color-error);
}

.card-percent {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.card-percent.warning {
  color: var(--color-warning);
}

.card-percent.over {
  color: var(--color-error);
}
</style>
