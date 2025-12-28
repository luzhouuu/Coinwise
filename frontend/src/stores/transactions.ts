/**
 * Transactions store using Pinia Composition API.
 */

import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import {
  createTransaction as apiCreateTransaction,
  deleteTransaction as apiDeleteTransaction,
  getTransactions,
  updateTransaction as apiUpdateTransaction,
  type Transaction,
  type TransactionCreate,
  type TransactionFilters,
  type TransactionUpdate,
} from '@/api/transactions';

export const useTransactionStore = defineStore('transactions', () => {
  // State
  const transactions = ref<Transaction[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
  });
  const filters = ref<TransactionFilters>({
    start_date: undefined,
    end_date: undefined,
    category_id: undefined,
    transaction_type: undefined,
    search: '',
    sort_by: 'transaction_date',
    sort_order: 'desc',
  });

  // Getters
  const totalPages = computed(() =>
    Math.ceil(pagination.value.total / pagination.value.pageSize)
  );

  const hasMore = computed(() => pagination.value.page < totalPages.value);

  // Actions
  async function fetchTransactions(): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      const response = await getTransactions({
        ...filters.value,
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
      });

      transactions.value = response.data;
      pagination.value.total = response.total;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch transactions';
    } finally {
      loading.value = false;
    }
  }

  function setFilter<K extends keyof TransactionFilters>(
    key: K,
    value: TransactionFilters[K]
  ): void {
    filters.value[key] = value;
    pagination.value.page = 1;
    fetchTransactions();
  }

  function setPage(page: number): void {
    pagination.value.page = page;
    fetchTransactions();
  }

  function resetFilters(): void {
    filters.value = {
      start_date: undefined,
      end_date: undefined,
      category_id: undefined,
      transaction_type: undefined,
      search: '',
      sort_by: 'transaction_date',
      sort_order: 'desc',
    };
    pagination.value.page = 1;
    fetchTransactions();
  }

  async function createTransaction(data: TransactionCreate): Promise<Transaction | null> {
    try {
      const transaction = await apiCreateTransaction(data);
      // Refresh the list to show the new transaction
      await fetchTransactions();
      return transaction;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create transaction';
      return null;
    }
  }

  async function updateTransaction(
    id: number,
    data: TransactionUpdate
  ): Promise<Transaction | null> {
    try {
      const transaction = await apiUpdateTransaction(id, data);
      // Update the transaction in the list
      const index = transactions.value.findIndex((t) => t.id === id);
      if (index !== -1) {
        transactions.value[index] = transaction;
      }
      return transaction;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update transaction';
      return null;
    }
  }

  async function deleteTransaction(id: number): Promise<boolean> {
    try {
      await apiDeleteTransaction(id);
      transactions.value = transactions.value.filter((t) => t.id !== id);
      pagination.value.total -= 1;
      return true;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete transaction';
      return false;
    }
  }

  return {
    // State
    transactions,
    loading,
    error,
    pagination,
    filters,
    // Getters
    totalPages,
    hasMore,
    // Actions
    fetchTransactions,
    setFilter,
    setPage,
    resetFilters,
    createTransaction,
    updateTransaction,
    deleteTransaction,
  };
});
