/**
 * Statistics store using Pinia Composition API.
 */

import { ref } from 'vue';
import { defineStore } from 'pinia';
import {
  type CategoryStat,
  getByCategory,
  getCategories,
  getLatestMonth,
  getSummary,
  getTrend,
  type LatestMonth,
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
  const latestMonth = ref<LatestMonth | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Date range state
  const dateRange = ref({
    start: getDefaultStartDate(),
    end: getDefaultEndDate(),
  });

  // Current granularity for trend data
  const currentGranularity = ref<'day' | 'week' | 'month'>('month');

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

  async function fetchLatestMonth(): Promise<LatestMonth> {
    try {
      latestMonth.value = await getLatestMonth();
      return latestMonth.value;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch latest month';
      const now = new Date();
      return { year: now.getFullYear(), month: now.getMonth() + 1 };
    }
  }

  async function fetchAll(granularity?: 'day' | 'week' | 'month'): Promise<void> {
    loading.value = true;
    error.value = null;

    // Update granularity if provided
    if (granularity) {
      currentGranularity.value = granularity;
    }

    try {
      await Promise.all([
        fetchSummary(),
        fetchCategoryStats(),
        fetchTrendData(currentGranularity.value),
        fetchCategories(),
      ]);
    } finally {
      loading.value = false;
    }
  }

  function setDateRange(start: string, end: string, granularity?: 'day' | 'week' | 'month'): void {
    dateRange.value = { start, end };
    fetchAll(granularity);
  }

  return {
    // State
    summary,
    categoryStats,
    trendData,
    categories,
    latestMonth,
    loading,
    error,
    dateRange,
    currentGranularity,
    // Actions
    fetchSummary,
    fetchCategoryStats,
    fetchTrendData,
    fetchCategories,
    fetchLatestMonth,
    fetchAll,
    setDateRange,
  };
});
