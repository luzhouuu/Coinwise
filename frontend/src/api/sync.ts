/**
 * Sync API client.
 */

import apiClient, { API_BASE_URL } from './index';

export type SyncStatus = 'idle' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface SyncStartRequest {
  since_date?: string;
  dry_run?: boolean;
}

export interface SyncStatusResponse {
  status: SyncStatus;
  started_at: string | null;
  progress: number;
  current_account: string | null;
  processed_count: number;
  skipped_count: number;
  error_count: number;
  logs: string[];
}

/**
 * Start a new sync task.
 */
export async function startSync(
  request: SyncStartRequest = {}
): Promise<SyncStatusResponse> {
  const response = await apiClient.post<SyncStatusResponse>('/sync/start', request);
  return response.data;
}

/**
 * Get current sync status.
 */
export async function getSyncStatus(): Promise<SyncStatusResponse> {
  const response = await apiClient.get<SyncStatusResponse>('/sync/status');
  return response.data;
}

/**
 * Cancel the running sync task.
 */
export async function cancelSync(): Promise<{ message: string; cancelled: boolean }> {
  const response = await apiClient.post('/sync/cancel');
  return response.data;
}

/**
 * Create WebSocket connection for real-time sync updates.
 */
export function createSyncWebSocket(
  onMessage: (data: { type: string; message?: string; progress?: number; status?: SyncStatus }) => void,
  onClose?: () => void
): WebSocket {
  const wsUrl = API_BASE_URL.replace(/^http/, 'ws') + '/sync/ws';
  const ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error('WebSocket message parse error:', e);
    }
  };

  ws.onclose = () => {
    if (onClose) onClose();
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  return ws;
}
