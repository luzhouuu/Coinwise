/**
 * Configuration API client.
 */

import apiClient from './index';

export interface EmailAccount {
  id: number;
  email: string;
  imap_server: string;
  imap_port: number;
  bank_type: string;
  is_active: boolean;
  last_sync_at: string | null;
}

export interface EmailAccountCreate {
  email: string;
  password: string;
  imap_server: string;
  imap_port: number;
  bank_type: string;
}

export interface EmailAccountUpdate {
  email?: string;
  password?: string;
  imap_server?: string;
  imap_port?: number;
  bank_type?: string;
  is_active?: boolean;
}

export interface Category {
  id: number;
  name: string;
  icon: string | null;
  color: string | null;
  parent_id: number | null;
}

export interface CategoryCreate {
  name: string;
  icon?: string | null;
  color?: string | null;
  parent_id?: number | null;
}

export interface CategoryRule {
  id: number;
  pattern: string;
  category_id: number;
  category_name: string | null;
  priority: number;
}

export interface CategoryRuleCreate {
  pattern: string;
  category_id: number;
  priority?: number;
}

export interface CategoryRulesResponse {
  rules: CategoryRule[];
}

// Email Accounts
export async function getEmailAccounts(): Promise<EmailAccount[]> {
  const response = await apiClient.get<EmailAccount[]>('/config/email-accounts');
  return response.data;
}

export async function createEmailAccount(
  account: EmailAccountCreate
): Promise<EmailAccount> {
  const response = await apiClient.post<EmailAccount>(
    '/config/email-accounts',
    account
  );
  return response.data;
}

export async function updateEmailAccount(
  id: number,
  data: EmailAccountUpdate
): Promise<EmailAccount> {
  const response = await apiClient.put<EmailAccount>(
    `/config/email-accounts/${id}`,
    data
  );
  return response.data;
}

export async function deleteEmailAccount(id: number): Promise<void> {
  await apiClient.delete(`/config/email-accounts/${id}`);
}

// Categories
export async function getCategories(): Promise<Category[]> {
  const response = await apiClient.get<Category[]>('/config/categories');
  return response.data;
}

export async function createCategory(data: CategoryCreate): Promise<Category> {
  const response = await apiClient.post<Category>('/config/categories', data);
  return response.data;
}

export async function deleteCategory(id: number): Promise<void> {
  await apiClient.delete(`/config/categories/${id}`);
}

// Category Rules
export async function getCategoryRules(): Promise<CategoryRulesResponse> {
  const response = await apiClient.get<CategoryRulesResponse>('/config/category-rules');
  return response.data;
}

export async function createCategoryRule(
  data: CategoryRuleCreate
): Promise<CategoryRule> {
  const response = await apiClient.post<CategoryRule>(
    '/config/category-rules',
    data
  );
  return response.data;
}

export async function updateCategoryRule(
  id: number,
  data: Partial<CategoryRuleCreate>
): Promise<CategoryRule> {
  const response = await apiClient.put<CategoryRule>(
    `/config/category-rules/${id}`,
    data
  );
  return response.data;
}

export async function deleteCategoryRule(id: number): Promise<void> {
  await apiClient.delete(`/config/category-rules/${id}`);
}
