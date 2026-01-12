/**
 * API client configuration using Axios.
 */

import axios, { type AxiosError, type AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const TOKEN_KEY = 'coinwise_token';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth header
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      // Don't redirect if already on login page or auth endpoints
      const isAuthEndpoint = error.config?.url?.includes('/auth/');
      if (!isAuthEndpoint && window.location.pathname !== '/login') {
        localStorage.removeItem(TOKEN_KEY);
        window.location.href = '/login';
      }
    }

    const message =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      'Network error';

    console.error('API Error:', message);

    return Promise.reject(error);
  }
);

export default apiClient;
export { API_BASE_URL };
