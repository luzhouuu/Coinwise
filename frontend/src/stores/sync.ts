/**
 * Sync store using Pinia Composition API.
 */

import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import {
  cancelSync as apiCancelSync,
  createSyncWebSocket,
  getSyncStatus,
  startSync as apiStartSync,
  type SyncStartRequest,
  type SyncStatus,
} from '@/api/sync';

export const useSyncStore = defineStore('sync', () => {
  // State
  const status = ref<SyncStatus>('idle');
  const progress = ref(0);
  const currentAccount = ref<string | null>(null);
  const processedCount = ref(0);
  const skippedCount = ref(0);
  const errorCount = ref(0);
  const logs = ref<string[]>([]);
  const startedAt = ref<string | null>(null);

  let ws: WebSocket | null = null;

  // Getters
  const isRunning = computed(() => status.value === 'running');
  const isCompleted = computed(() => status.value === 'completed');
  const isFailed = computed(() => status.value === 'failed');

  // Actions
  function updateFromResponse(data: {
    status: SyncStatus;
    started_at: string | null;
    progress: number;
    current_account: string | null;
    processed_count: number;
    skipped_count: number;
    error_count: number;
    logs: string[];
  }): void {
    status.value = data.status;
    startedAt.value = data.started_at;
    progress.value = data.progress;
    currentAccount.value = data.current_account;
    processedCount.value = data.processed_count;
    skippedCount.value = data.skipped_count;
    errorCount.value = data.error_count;
    logs.value = data.logs;
  }

  async function fetchStatus(): Promise<void> {
    const response = await getSyncStatus();
    updateFromResponse(response);
  }

  async function startSync(request: SyncStartRequest = {}): Promise<void> {
    // Clear previous logs
    logs.value = [];
    progress.value = 0;

    // Start sync
    const response = await apiStartSync(request);
    updateFromResponse(response);

    // Connect WebSocket for real-time updates
    connectWebSocket();
  }

  function connectWebSocket(): void {
    if (ws) {
      ws.close();
    }

    ws = createSyncWebSocket(
      (data) => {
        if (data.type === 'log' && data.message) {
          logs.value = [...logs.value, data.message];
          // Keep only last 100 logs
          if (logs.value.length > 100) {
            logs.value = logs.value.slice(-100);
          }
        }
        if (data.type === 'progress' && data.progress !== undefined) {
          progress.value = data.progress;
        }
        if (data.type === 'status' && data.status) {
          status.value = data.status;

          // Disconnect when sync is done
          if (['completed', 'failed', 'cancelled'].includes(data.status)) {
            disconnectWebSocket();
          }
        }
      },
      () => {
        ws = null;
      }
    );
  }

  function disconnectWebSocket(): void {
    if (ws) {
      ws.close();
      ws = null;
    }
  }

  async function cancelSync(): Promise<boolean> {
    try {
      await apiCancelSync();
      disconnectWebSocket();
      return true;
    } catch (e) {
      return false;
    }
  }

  function clearLogs(): void {
    logs.value = [];
  }

  return {
    // State
    status,
    progress,
    currentAccount,
    processedCount,
    skippedCount,
    errorCount,
    logs,
    startedAt,
    // Getters
    isRunning,
    isCompleted,
    isFailed,
    // Actions
    fetchStatus,
    startSync,
    cancelSync,
    clearLogs,
    connectWebSocket,
    disconnectWebSocket,
  };
});
