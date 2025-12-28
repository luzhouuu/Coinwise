/**
 * Budget goals store using Pinia Composition API.
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  type BudgetGoal,
  type BudgetGoalCreate,
  type BudgetGoalUpdate,
  type BudgetSummary,
  type MonthComparisonResponse,
  getBudgets,
  createBudget,
  updateBudget,
  deleteBudget,
  getBudgetSummary,
  getMonthComparison,
  copyRecurringBudgets,
} from '@/api/budgets'

export const useBudgetStore = defineStore('budgets', () => {
  // State
  const budgets = ref<BudgetGoal[]>([])
  const summary = ref<BudgetSummary | null>(null)
  const comparison = ref<MonthComparisonResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Selected month state
  const selectedMonth = ref({
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
  })

  // Computed
  const monthLabel = computed(() => {
    const date = new Date(selectedMonth.value.year, selectedMonth.value.month - 1)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })
  })

  const monthLabelEn = computed(() => {
    const date = new Date(selectedMonth.value.year, selectedMonth.value.month - 1)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
  })

  const hasOverBudget = computed(() => {
    if (!summary.value) return false
    return summary.value.items.some((item) => item.percentage_used > 100)
  })

  // Actions
  async function fetchBudgets(): Promise<void> {
    try {
      budgets.value = await getBudgets(
        selectedMonth.value.year,
        selectedMonth.value.month
      )
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch budgets'
    }
  }

  async function fetchSummary(): Promise<void> {
    try {
      summary.value = await getBudgetSummary(
        selectedMonth.value.year,
        selectedMonth.value.month
      )
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch summary'
    }
  }

  async function fetchComparison(months: number = 3): Promise<void> {
    try {
      comparison.value = await getMonthComparison(months)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch comparison'
    }
  }

  async function fetchAll(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      await Promise.all([fetchBudgets(), fetchSummary(), fetchComparison()])
    } finally {
      loading.value = false
    }
  }

  async function addBudget(data: BudgetGoalCreate): Promise<BudgetGoal | null> {
    try {
      const budget = await createBudget(data)
      budgets.value.push(budget)
      await fetchSummary() // Refresh summary
      return budget
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create budget'
      return null
    }
  }

  async function editBudget(
    id: number,
    data: BudgetGoalUpdate
  ): Promise<BudgetGoal | null> {
    try {
      const budget = await updateBudget(id, data)
      const index = budgets.value.findIndex((b) => b.id === id)
      if (index !== -1) {
        budgets.value[index] = budget
      }
      await fetchSummary() // Refresh summary
      return budget
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update budget'
      return null
    }
  }

  async function removeBudget(id: number): Promise<boolean> {
    try {
      await deleteBudget(id)
      budgets.value = budgets.value.filter((b) => b.id !== id)
      await fetchSummary() // Refresh summary
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete budget'
      return false
    }
  }

  async function copyFromPreviousMonth(): Promise<number> {
    try {
      const result = await copyRecurringBudgets(
        selectedMonth.value.year,
        selectedMonth.value.month
      )
      if (result.count > 0) {
        await fetchAll()
      }
      return result.count
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to copy budgets'
      return 0
    }
  }

  function setMonth(year: number, month: number): void {
    selectedMonth.value = { year, month }
    fetchAll()
  }

  function navigateMonth(direction: 1 | -1): void {
    let { year, month } = selectedMonth.value
    month += direction

    if (month > 12) {
      month = 1
      year += 1
    } else if (month < 1) {
      month = 12
      year -= 1
    }

    setMonth(year, month)
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    budgets,
    summary,
    comparison,
    loading,
    error,
    selectedMonth,
    // Computed
    monthLabel,
    monthLabelEn,
    hasOverBudget,
    // Actions
    fetchBudgets,
    fetchSummary,
    fetchComparison,
    fetchAll,
    addBudget,
    editBudget,
    removeBudget,
    copyFromPreviousMonth,
    setMonth,
    navigateMonth,
    clearError,
  }
})
