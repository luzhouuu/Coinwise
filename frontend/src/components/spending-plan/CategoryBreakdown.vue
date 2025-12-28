<script setup lang="ts">
import { computed } from 'vue'
import { useBudgetStore } from '@/stores/budgets'
import { useI18nStore } from '@/stores/i18n'
import { ChartCard, PieChart } from '@/components/charts'

const budgetStore = useBudgetStore()
const i18n = useI18nStore()

const hasData = computed(() => {
  return budgetStore.summary && budgetStore.summary.items.length > 0
})

const chartLabels = computed(() => {
  if (!budgetStore.summary) return []
  return budgetStore.summary.items.map((item) => item.category_name)
})

const chartData = computed(() => {
  if (!budgetStore.summary) return []
  return budgetStore.summary.items.map((item) => item.spent_amount)
})

const chartColors = computed(() => {
  if (!budgetStore.summary) return []
  return budgetStore.summary.items.map(
    (item) => item.category_color || '#8E8E93'
  )
})
</script>

<template>
  <ChartCard :title="i18n.t('chart.category_breakdown')" height="300px">
    <div v-if="hasData" class="chart-container">
      <PieChart
        :labels="chartLabels"
        :data="chartData"
        :colors="chartColors"
        :donut="true"
      />
    </div>
    <div v-else class="empty-state">
      <span class="empty-text">{{ i18n.t('chart.no_data') }}</span>
    </div>
  </ChartCard>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.empty-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}
</style>
