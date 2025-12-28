/**
 * Statistics store using Pinia Composition API.
 */

import { ref } from 'vue';
import { defineStore } from 'pinia';
import {
  type CategoryStat,
  getByCategory,
  getCategories,
  getSummary,
  getTrend,
  type StatisticsSummary,
  type TrendDataPoint,
  type Category,
} from '@/api/statistics';

export const useStatisticsStore = defineStore('statistics', () => {
  // State
  const summary = ref<StatisticsSummary | null>(null);
  const categoryStats = ref<CategoryStat[]>([]);
  const trendData = ref<TrendDataPoint[]>([]);
  const categories = ref<Category[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Date range state
  const dateRange = ref({
    start: getDefaultStartDate(),
    end: getDefaultEndDate(),
  });

  // Helper functions
  function getDefaultStartDate(): string {
    const date = new Date();
    date.setMonth(date.getMonth() - 1);
    date.setDate(1);
    return date.toISOString().split('T')[0] as string;
  }

  function getDefaultEndDate(): string {
    return new Date().toISOString().split('T')[0] as string;
  }

  // Actions
  async function fetchSummary(): Promise<void> {
    try {
      summary.value = await getSummary(dateRange.value.start, dateRange.value.end);
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch summary';
    }
  }

  async function fetchCategoryStats(): Promise<void> {
    try {
      categoryStats.value = await getByCategory(
        dateRange.value.start,
        dateRange.value.end
      );
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch category stats';
    }
  }

  async function fetchTrendData(
    granularity: 'day' | 'week' | 'month' = 'month'
  ): Promise<void> {
    try {
      trendData.value = await getTrend(
        dateRange.value.start,
        dateRange.value.end,
        granularity
      );
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch trend data';
    }
  }

  async function fetchCategories(): Promise<void> {
    try {
      categories.value = await getCategories();
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch categories';
    }
  }

  async function fetchAll(): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await Promise.all([
        fetchSummary(),
        fetchCategoryStats(),
        fetchTrendData(),
        fetchCategories(),
      ]);
    } finally {
      loading.value = false;
    }
  }

  function setDateRange(start: string, end: string): void {
    dateRange.value = { start, end };
    fetchAll();
  }

  return {
    // State
    summary,
    categoryStats,
    trendData,
    categories,
    loading,
    error,
    dateRange,
    // Actions
    fetchSummary,
    fetchCategoryStats,
    fetchTrendData,
    fetchCategories,
    fetchAll,
    setDateRange,
  };
});
