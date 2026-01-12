/**
 * Chat API client for bill assistant.
 */

import apiClient from './index';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history?: ChatMessage[];
}

export interface ChatResponse {
  reply: string;
  success: boolean;
}

export interface CategoriesResponse {
  categories: string[];
}

/**
 * Send a message to the chat assistant.
 */
export async function sendMessage(message: string, history?: ChatMessage[]): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/chat/message', {
    message,
    history,
  });
  return response.data;
}

/**
 * Get available categories for reference.
 */
export async function getCategories(): Promise<CategoriesResponse> {
  const response = await apiClient.get<CategoriesResponse>('/chat/categories');
  return response.data;
}
