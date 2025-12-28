/**
 * API client configuration using Axios.
 */

import axios, { type AxiosError, type AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const message =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      'Network error';

    console.error('API Error:', message);

    // You can add toast notification here
    return Promise.reject(error);
  }
);

export default apiClient;
export { API_BASE_URL };
