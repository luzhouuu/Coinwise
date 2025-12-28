/**
 * Transactions API client.
 */

import apiClient from './index';

export interface Transaction {
  id: number;
  transaction_date: string;
  amount: number;
  description: string;
  category_id: number | null;
  category_name: string | null;
  transaction_type: string;
  source_account: string | null;
  destination_account: string | null;
  tags: string[];
  notes: string | null;
  is_manual: boolean;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  transaction_date: string;
  amount: number;
  description: string;
  category_id?: number | null;
  transaction_type: string;
  source_account?: string | null;
  destination_account?: string | null;
  tags?: string[];
  notes?: string | null;
}

export interface TransactionUpdate {
  transaction_date?: string;
  amount?: number;
  description?: string;
  category_id?: number | null;
  transaction_type?: string;
  source_account?: string | null;
  destination_account?: string | null;
  tags?: string[];
  notes?: string | null;
}

export interface TransactionListResponse {
  data: Transaction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TransactionFilters {
  start_date?: string;
  end_date?: string;
  category_id?: number;
  transaction_type?: string;
  search?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: string;
}

/**
 * Get paginated list of transactions.
 */
export async function getTransactions(
  filters: TransactionFilters = {}
): Promise<TransactionListResponse> {
  const params = new URLSearchParams();

  if (filters.start_date) params.append('start_date', filters.start_date);
  if (filters.end_date) params.append('end_date', filters.end_date);
  if (filters.category_id) params.append('category_id', filters.category_id.toString());
  if (filters.transaction_type) params.append('transaction_type', filters.transaction_type);
  if (filters.search) params.append('search', filters.search);
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.page_size) params.append('page_size', filters.page_size.toString());
  if (filters.sort_by) params.append('sort_by', filters.sort_by);
  if (filters.sort_order) params.append('sort_order', filters.sort_order);

  const response = await apiClient.get<TransactionListResponse>(
    `/transactions?${params.toString()}`
  );
  return response.data;
}

/**
 * Get a single transaction by ID.
 */
export async function getTransaction(id: number): Promise<Transaction> {
  const response = await apiClient.get<Transaction>(`/transactions/${id}`);
  return response.data;
}

/**
 * Create a new transaction.
 */
export async function createTransaction(
  data: TransactionCreate
): Promise<Transaction> {
  const response = await apiClient.post<Transaction>('/transactions', data);
  return response.data;
}

/**
 * Update an existing transaction.
 */
export async function updateTransaction(
  id: number,
  data: TransactionUpdate
): Promise<Transaction> {
  const response = await apiClient.put<Transaction>(`/transactions/${id}`, data);
  return response.data;
}

/**
 * Delete a transaction.
 */
export async function deleteTransaction(id: number): Promise<void> {
  await apiClient.delete(`/transactions/${id}`);
}
