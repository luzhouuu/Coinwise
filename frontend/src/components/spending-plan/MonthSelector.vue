<script setup lang="ts">
import { computed } from 'vue'
import { useBudgetStore } from '@/stores/budgets'
import { useI18nStore } from '@/stores/i18n'

const budgetStore = useBudgetStore()
const i18n = useI18nStore()

const displayMonth = computed(() => {
  const { year, month } = budgetStore.selectedMonth
  if (i18n.isZh) {
    return `${year}年${i18n.formatMonth(month)}`
  }
  return `${i18n.formatMonth(month)} ${year}`
})

function prevMonth() {
  budgetStore.navigateMonth(-1)
}

function nextMonth() {
  budgetStore.navigateMonth(1)
}
</script>

<template>
  <div class="month-selector">
    <button class="month-nav-btn" @click="prevMonth" :title="i18n.t('common.previous')">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
    <span class="month-display">{{ displayMonth }}</span>
    <button class="month-nav-btn" @click="nextMonth" :title="i18n.t('common.next')">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </div>
</template>

<style scoped>
.month-selector {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.month-nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.month-nav-btn:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.month-display {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  min-width: 160px;
  text-align: center;
}
</style>
