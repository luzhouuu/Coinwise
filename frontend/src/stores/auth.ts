/**
 * Authentication store using Pinia Composition API.
 */

import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { login as apiLogin, verifyToken } from '@/api/auth';

const TOKEN_KEY = 'coinwise_token';

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY));
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!token.value);

  // Actions
  async function login(username: string, password: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiLogin({ username, password });
      token.value = response.access_token;
      localStorage.setItem(TOKEN_KEY, response.access_token);
      return true;
    } catch (e: any) {
      error.value = e.response?.data?.detail || '登录失败，请重试';
      return false;
    } finally {
      loading.value = false;
    }
  }

  function logout(): void {
    token.value = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  async function checkAuth(): Promise<boolean> {
    if (!token.value) return false;

    const valid = await verifyToken();
    if (!valid) {
      logout();
    }
    return valid;
  }

  function getToken(): string | null {
    return token.value;
  }

  return {
    // State
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    // Actions
    login,
    logout,
    checkAuth,
    getToken,
  };
});
