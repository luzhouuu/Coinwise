/**
 * Statistics API client.
 */

import apiClient from './index';

export interface StatisticsSummary {
  total_expense: number;
  total_income: number;
  transaction_count: number;
  start_date: string;
  end_date: string;
}

export interface CategoryStat {
  category: string;
  amount: number;
  count: number;
  percentage: number;
}

export interface TrendDataPoint {
  date: string;
  amount: number;
  count: number;
}

export interface Category {
  id: string;
  name: string;
}

/**
 * Get summary statistics.
 */
export async function getSummary(
  startDate: string,
  endDate: string
): Promise<StatisticsSummary> {
  const response = await apiClient.get<StatisticsSummary>('/statistics/summary', {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
}

/**
 * Get category breakdown.
 */
export async function getByCategory(
  startDate: string,
  endDate: string
): Promise<CategoryStat[]> {
  const response = await apiClient.get<CategoryStat[]>('/statistics/by-category', {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
}

/**
 * Get expense trend.
 */
export async function getTrend(
  startDate: string,
  endDate: string,
  granularity: 'day' | 'week' | 'month' = 'month'
): Promise<TrendDataPoint[]> {
  const response = await apiClient.get<TrendDataPoint[]>('/statistics/trend', {
    params: { start_date: startDate, end_date: endDate, granularity },
  });
  return response.data;
}

/**
 * Get all categories.
 */
export async function getCategories(): Promise<Category[]> {
  const response = await apiClient.get<Category[]>('/statistics/categories');
  return response.data;
}
