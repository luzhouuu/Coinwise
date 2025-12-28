<script setup lang="ts">
/**
 * Dashboard view with statistics overview and charts.
 */
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStatisticsStore } from '@/stores/statistics'
import { useI18nStore } from '@/stores/i18n'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { ChartCard, PieChart, AreaChart, BarChart } from '@/components/charts'
import SpendingAnalysis from '@/components/dashboard/SpendingAnalysis.vue'

const store = useStatisticsStore()
const i18n = useI18nStore()
const router = useRouter()

// Date range options
const dateRangeOptions = [
  { label: '本月', value: 'month' },
  { label: '近3月', value: '3months' },
  { label: '近6月', value: '6months' },
  { label: '今年', value: 'year' },
]
const selectedRange = ref('3months')

onMounted(() => {
  updateDateRange()
})

function updateDateRange() {
  const now = new Date()
  let start: Date

  switch (selectedRange.value) {
    case 'month':
      start = new Date(now.getFullYear(), now.getMonth(), 1)
      break
    case '3months':
      start = new Date(now.getFullYear(), now.getMonth() - 2, 1)
      break
    case '6months':
      start = new Date(now.getFullYear(), now.getMonth() - 5, 1)
      break
    case 'year':
      start = new Date(now.getFullYear(), 0, 1)
      break
    default:
      start = new Date(now.getFullYear(), now.getMonth() - 2, 1)
  }

  const startDate = start.toISOString().split('T')[0] ?? ''
  const endDate = now.toISOString().split('T')[0] ?? ''
  store.setDateRange(startDate, endDate)
}

function onRangeChange() {
  updateDateRange()
}

// Format currency
function formatCurrency(value: number): string {
  return i18n.formatCurrency(value)
}

// Computed stats
const avgDailySpend = computed(() => {
  if (!store.summary) return 0
  const start = new Date(store.summary.start_date)
  const end = new Date(store.summary.end_date)
  const days = Math.max(1, Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)))
  return store.summary.total_expense / days
})

const netBalance = computed(() => {
  if (!store.summary) return 0
  return store.summary.total_income - store.summary.total_expense
})

// Chart data
const categoryLabels = computed(() => store.categoryStats.map(c => c.category))
const categoryData = computed(() => store.categoryStats.map(c => c.amount))
const categoryColors = computed((): string[] => {
  const colors = ['#007AFF', '#34C759', '#FF9500', '#FF3B30', '#5AC8FA', '#AF52DE', '#FF2D55', '#A2845E']
  return store.categoryStats.map((_, i) => colors[i % colors.length] ?? '#007AFF')
})

const trendLabels = computed((): string[] => store.trendData.map(t => {
  const parts = t.date.split('-')
  const month = parts[1] ?? ''
  return i18n.isZh ? `${month}月` : t.date
}))
const trendDatasets = computed(() => [{
  label: i18n.isZh ? '支出' : 'Expense',
  data: store.trendData.map(t => t.amount),
  color: '#007AFF'
}])

// Top categories for list
const topCategories = computed(() => store.categoryStats.slice(0, 5))

function goToTransactions() {
  router.push('/transactions')
}

function goToSpendingPlan() {
  router.push('/spending-plan')
}
</script>

<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <h1 class="page-title">{{ i18n.isZh ? '数据概览' : 'Overview' }}</h1>
      <div class="date-range-selector">
        <button
          v-for="opt in dateRangeOptions"
          :key="opt.value"
          class="range-btn"
          :class="{ active: selectedRange === opt.value }"
          @click="selectedRange = opt.value; onRangeChange()"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-container">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Summary Cards Row 1 -->
      <div class="summary-grid">
        <div class="summary-card expense">
          <div class="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2v20M2 12h20" stroke="currentColor" stroke-width="2" stroke-linecap="round" transform="rotate(45 12 12)" />
            </svg>
          </div>
          <div class="card-content">
            <span class="card-label">{{ i18n.isZh ? '总支出' : 'Total Expense' }}</span>
            <span class="card-value expense-value">{{ formatCurrency(store.summary?.total_expense || 0) }}</span>
          </div>
        </div>

        <div class="summary-card income">
          <div class="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2v20M2 12h20" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </div>
          <div class="card-content">
            <span class="card-label">{{ i18n.isZh ? '总收入' : 'Total Income' }}</span>
            <span class="card-value income-value">{{ formatCurrency(store.summary?.total_income || 0) }}</span>
          </div>
        </div>

        <div class="summary-card balance" :class="{ negative: netBalance < 0 }">
          <div class="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M3 3v18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 16l4-4 4 4 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="card-content">
            <span class="card-label">{{ i18n.isZh ? '净余额' : 'Net Balance' }}</span>
            <span class="card-value" :class="{ negative: netBalance < 0 }">{{ formatCurrency(netBalance) }}</span>
          </div>
        </div>

        <div class="summary-card count">
          <div class="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </div>
          <div class="card-content">
            <span class="card-label">{{ i18n.isZh ? '交易笔数' : 'Transactions' }}</span>
            <span class="card-value">{{ store.summary?.transaction_count || 0 }}</span>
          </div>
        </div>

        <div class="summary-card avg">
          <div class="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="card-content">
            <span class="card-label">{{ i18n.isZh ? '日均支出' : 'Daily Avg' }}</span>
            <span class="card-value">{{ formatCurrency(avgDailySpend) }}</span>
          </div>
        </div>

        <div class="summary-card categories">
          <div class="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2l-5.5 9h11L12 2zm0 3.84L13.93 9h-3.87L12 5.84zM17.5 13c-2.49 0-4.5 2.01-4.5 4.5s2.01 4.5 4.5 4.5 4.5-2.01 4.5-4.5-2.01-4.5-4.5-4.5zm0 7c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5zM3 21.5h8v-8H3v8zm2-6h4v4H5v-4z" fill="currentColor"/>
            </svg>
          </div>
          <div class="card-content">
            <span class="card-label">{{ i18n.isZh ? '消费分类' : 'Categories' }}</span>
            <span class="card-value">{{ store.categoryStats.length }}</span>
          </div>
        </div>
      </div>

      <!-- AI Analysis -->
      <div class="analysis-row">
        <SpendingAnalysis />
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <!-- Spending Trend Chart -->
        <ChartCard :title="i18n.isZh ? '支出趋势' : 'Spending Trend'" height="280px">
          <template #actions>
            <button class="chart-action-btn" @click="goToSpendingPlan">
              {{ i18n.isZh ? '查看预算' : 'View Budget' }}
            </button>
          </template>
          <div v-if="store.trendData.length > 0" class="chart-container">
            <AreaChart
              :labels="trendLabels"
              :datasets="trendDatasets"
              :show-legend="false"
              :smooth="true"
              :fill-opacity="0.2"
            />
          </div>
          <div v-else class="chart-empty">
            <span>{{ i18n.isZh ? '暂无数据' : 'No data' }}</span>
          </div>
        </ChartCard>

        <!-- Category Pie Chart -->
        <ChartCard :title="i18n.isZh ? '分类占比' : 'Category Breakdown'" height="280px">
          <div v-if="store.categoryStats.length > 0" class="chart-container">
            <PieChart
              :labels="categoryLabels"
              :data="categoryData"
              :colors="categoryColors"
              :donut="true"
              :show-legend="true"
            />
          </div>
          <div v-else class="chart-empty">
            <span>{{ i18n.isZh ? '暂无数据' : 'No data' }}</span>
          </div>
        </ChartCard>
      </div>

      <!-- Bottom Row -->
      <div class="bottom-row">
        <!-- Top Categories List -->
        <div class="card category-card">
          <div class="card-header">
            <h3 class="card-title">{{ i18n.isZh ? 'Top 5 消费分类' : 'Top 5 Categories' }}</h3>
          </div>
          <div v-if="topCategories.length > 0" class="category-list">
            <div
              v-for="(cat, index) in topCategories"
              :key="cat.category"
              class="category-item"
            >
              <div class="category-rank">{{ index + 1 }}</div>
              <div class="category-info">
                <span
                  class="category-dot"
                  :style="{ background: categoryColors[index] }"
                />
                <span class="category-name">{{ cat.category }}</span>
              </div>
              <div class="category-stats">
                <span class="category-amount">{{ formatCurrency(cat.amount) }}</span>
                <span class="category-percent">{{ cat.percentage }}%</span>
              </div>
              <div class="category-bar">
                <div
                  class="category-bar-fill"
                  :style="{
                    width: `${cat.percentage}%`,
                    background: categoryColors[index],
                  }"
                />
              </div>
            </div>
          </div>
          <div v-else class="empty-list">
            <span>{{ i18n.isZh ? '暂无消费记录' : 'No spending records' }}</span>
          </div>
        </div>

        <!-- Monthly Comparison Bar Chart -->
        <div class="card trend-card">
          <div class="card-header">
            <h3 class="card-title">{{ i18n.isZh ? '月度对比' : 'Monthly Comparison' }}</h3>
            <button class="chart-action-btn" @click="goToTransactions">
              {{ i18n.isZh ? '查看全部' : 'View All' }}
            </button>
          </div>
          <div v-if="store.trendData.length > 0" class="bar-chart-container">
            <BarChart
              :labels="trendLabels"
              :datasets="[{
                label: i18n.isZh ? '支出' : 'Expense',
                data: store.trendData.map(t => t.amount),
                color: '#007AFF'
              }]"
              :show-legend="false"
            />
          </div>
          <div v-else class="empty-list">
            <span>{{ i18n.isZh ? '暂无数据' : 'No data' }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard {
  padding: var(--space-6);
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.date-range-selector {
  display: flex;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 2px;
}

.range-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  border: none;
  background: transparent;
  cursor: pointer;
}

.range-btn:hover {
  color: var(--color-text-primary);
}

.range-btn.active {
  background: var(--color-primary);
  color: white;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: var(--space-12);
}

/* Summary Cards */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* AI Analysis Row */
.analysis-row {
  margin-bottom: var(--space-6);
}

.summary-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.summary-card.expense .card-icon {
  background: var(--color-error-light);
  color: var(--color-error);
}

.summary-card.income .card-icon {
  background: var(--color-success-light);
  color: var(--color-success);
}

.summary-card.balance .card-icon {
  background: var(--color-info-light);
  color: var(--color-info);
}

.summary-card.balance.negative .card-icon {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.summary-card.count .card-icon {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.summary-card.avg .card-icon {
  background: #F3E8FF;
  color: #AF52DE;
}

.summary-card.categories .card-icon {
  background: #FFF4E5;
  color: #FF9500;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.card-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.card-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-value.expense-value {
  color: var(--color-error);
}

.card-value.income-value {
  color: var(--color-success);
}

.card-value.negative {
  color: var(--color-warning);
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

@media (max-width: 1024px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-container {
  width: 100%;
  height: 100%;
}

.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

.chart-action-btn {
  padding: var(--space-1) var(--space-3);
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  background: var(--color-primary-light);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.chart-action-btn:hover {
  background: var(--color-primary);
  color: white;
}

/* Bottom Row */
.bottom-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

@media (max-width: 1024px) {
  .bottom-row {
    grid-template-columns: 1fr;
  }
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

/* Category List */
.category-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.category-item {
  display: grid;
  grid-template-columns: 24px 1fr auto;
  grid-template-rows: auto auto;
  gap: var(--space-2);
  align-items: center;
}

.category-rank {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  background: var(--color-background);
  border-radius: var(--radius-full);
}

.category-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.category-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.category-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.category-stats {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  text-align: right;
}

.category-amount {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.category-percent {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  min-width: 40px;
}

.category-bar {
  grid-column: 2 / -1;
  height: 4px;
  background: var(--color-background);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.category-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

.bar-chart-container {
  height: 200px;
}

.empty-list {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 150px;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

@media (max-width: 768px) {
  .dashboard {
    padding: var(--space-4);
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .date-range-selector {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
