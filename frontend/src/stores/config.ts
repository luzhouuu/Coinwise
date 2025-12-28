/**
 * Configuration store using Pinia Composition API.
 */

import { ref } from 'vue';
import { defineStore } from 'pinia';
import {
  createEmailAccount as apiCreateEmailAccount,
  deleteEmailAccount as apiDeleteEmailAccount,
  getCategories,
  getCategoryRules,
  getEmailAccounts,
  type Category,
  type CategoryRule,
  type EmailAccount,
  type EmailAccountCreate,
} from '@/api/config';

export const useConfigStore = defineStore('config', () => {
  // State
  const emailAccounts = ref<EmailAccount[]>([]);
  const categories = ref<Category[]>([]);
  const categoryRules = ref<CategoryRule[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Actions
  async function fetchEmailAccounts(): Promise<void> {
    try {
      emailAccounts.value = await getEmailAccounts();
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch email accounts';
    }
  }

  async function addEmailAccount(account: EmailAccountCreate): Promise<boolean> {
    try {
      const newAccount = await apiCreateEmailAccount(account);
      emailAccounts.value.push(newAccount);
      return true;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to add email account';
      return false;
    }
  }

  async function deleteEmailAccount(id: number): Promise<boolean> {
    try {
      await apiDeleteEmailAccount(id);
      emailAccounts.value = emailAccounts.value.filter((a) => a.id !== id);
      return true;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete email account';
      return false;
    }
  }

  async function fetchCategories(): Promise<void> {
    try {
      categories.value = await getCategories();
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch categories';
    }
  }

  function getCategoryById(id: number | null): Category | undefined {
    if (id === null) return undefined;
    return categories.value.find((c) => c.id === id);
  }

  function getCategoryName(id: number | null): string {
    const category = getCategoryById(id);
    return category?.name || '';
  }

  async function fetchCategoryRules(): Promise<void> {
    try {
      const response = await getCategoryRules();
      categoryRules.value = response.rules;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch category rules';
    }
  }

  async function fetchAll(): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await Promise.all([
        fetchEmailAccounts(),
        fetchCategories(),
        fetchCategoryRules(),
      ]);
    } finally {
      loading.value = false;
    }
  }

  return {
    // State
    emailAccounts,
    categories,
    categoryRules,
    loading,
    error,
    // Actions
    fetchEmailAccounts,
    addEmailAccount,
    deleteEmailAccount,
    fetchCategories,
    getCategoryById,
    getCategoryName,
    fetchCategoryRules,
    fetchAll,
  };
});
