<script setup lang="ts">
import { computed } from 'vue'
import { useBudgetStore } from '@/stores/budgets'
import { useI18nStore } from '@/stores/i18n'
import { ChartCard, LineChart } from '@/components/charts'

const budgetStore = useBudgetStore()
const i18n = useI18nStore()

const hasData = computed(() => {
  return (
    budgetStore.comparison &&
    budgetStore.comparison.categories.length > 0
  )
})

const chartLabels = computed(() => {
  if (!budgetStore.comparison) return []
  return budgetStore.comparison.months.map((m) => {
    const [year, month] = m.split('-')
    if (i18n.isZh) {
      return `${month}月`
    }
    return new Date(Number(year), Number(month) - 1).toLocaleDateString('en-US', {
      month: 'short',
    })
  })
})

const chartDatasets = computed(() => {
  if (!budgetStore.comparison) return []
  return budgetStore.comparison.categories.slice(0, 6).map((cat) => ({
    label: cat.category_name,
    data: cat.data.map((d) => d.amount),
    color: cat.category_color || undefined,
  }))
})
</script>

<template>
  <ChartCard :title="i18n.t('chart.month_comparison')" height="300px">
    <div v-if="hasData" class="chart-container">
      <LineChart
        :labels="chartLabels"
        :datasets="chartDatasets"
        :show-legend="true"
        :smooth="true"
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
