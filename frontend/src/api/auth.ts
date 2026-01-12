/**
 * Authentication API client.
 */

import apiClient from './index';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/login', credentials);
  return response.data;
}

export async function verifyToken(): Promise<boolean> {
  try {
    await apiClient.get('/auth/verify');
    return true;
  } catch {
    return false;
  }
}
