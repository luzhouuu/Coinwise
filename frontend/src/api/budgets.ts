/**
 * Budget goals API client.
 */

import apiClient from './index'

export interface BudgetGoal {
  id: number
  category_id: number
  category_name: string
  category_color: string | null
  year: number
  month: number
  amount: number
  is_recurring: boolean
  created_at: string
  updated_at: string
}

export interface BudgetGoalCreate {
  category_id: number
  year: number
  month: number
  amount: number
  is_recurring?: boolean
}

export interface BudgetGoalUpdate {
  amount?: number
  is_recurring?: boolean
}

export interface BudgetSummaryItem {
  category_id: number
  category_name: string
  category_color: string | null
  budget_amount: number
  spent_amount: number
  remaining: number
  percentage_used: number
}

export interface BudgetSummary {
  year: number
  month: number
  total_budget: number
  total_spent: number
  total_remaining: number
  category_count: number
  items: BudgetSummaryItem[]
}

export interface MonthComparisonItem {
  month: string
  amount: number
}

export interface CategoryComparisonData {
  category_name: string
  category_color: string | null
  data: MonthComparisonItem[]
}

export interface MonthComparisonResponse {
  months: string[]
  categories: CategoryComparisonData[]
}

/**
 * Get all budget goals with optional filters.
 */
export async function getBudgets(
  year?: number,
  month?: number,
  categoryId?: number
): Promise<BudgetGoal[]> {
  const params: Record<string, number> = {}
  if (year) params.year = year
  if (month) params.month = month
  if (categoryId) params.category_id = categoryId

  const response = await apiClient.get<BudgetGoal[]>('/budgets', { params })
  return response.data
}

/**
 * Get a single budget goal.
 */
export async function getBudget(id: number): Promise<BudgetGoal> {
  const response = await apiClient.get<BudgetGoal>(`/budgets/${id}`)
  return response.data
}

/**
 * Create a new budget goal.
 */
export async function createBudget(data: BudgetGoalCreate): Promise<BudgetGoal> {
  const response = await apiClient.post<BudgetGoal>('/budgets', data)
  return response.data
}

/**
 * Update a budget goal.
 */
export async function updateBudget(
  id: number,
  data: BudgetGoalUpdate
): Promise<BudgetGoal> {
  const response = await apiClient.put<BudgetGoal>(`/budgets/${id}`, data)
  return response.data
}

/**
 * Delete a budget goal.
 */
export async function deleteBudget(id: number): Promise<void> {
  await apiClient.delete(`/budgets/${id}`)
}

/**
 * Get budget summary for a specific month.
 */
export async function getBudgetSummary(
  year: number,
  month: number
): Promise<BudgetSummary> {
  const response = await apiClient.get<BudgetSummary>('/budgets/summary', {
    params: { year, month },
  })
  return response.data
}

/**
 * Get month-over-month comparison data.
 */
export async function getMonthComparison(
  months: number = 3
): Promise<MonthComparisonResponse> {
  const response = await apiClient.get<MonthComparisonResponse>(
    '/budgets/comparison',
    { params: { months } }
  )
  return response.data
}

/**
 * Copy recurring budgets from previous month.
 */
export async function copyRecurringBudgets(
  year: number,
  month: number
): Promise<{ message: string; count: number }> {
  const response = await apiClient.post<{ message: string; count: number }>(
    '/budgets/copy-recurring',
    null,
    { params: { year, month } }
  )
  return response.data
}
