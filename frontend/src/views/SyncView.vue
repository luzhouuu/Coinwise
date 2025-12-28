<script setup lang="ts">
/**
 * Sync control view for managing bill synchronization.
 */
import { onMounted, onUnmounted, ref, computed } from 'vue';
import { useSyncStore } from '@/stores/sync';

const store = useSyncStore();

const sinceDate = ref('');
const dryRun = ref(false);

// Default to first day of last month
const defaultDate = computed(() => {
  const date = new Date();
  date.setMonth(date.getMonth() - 1);
  date.setDate(1);
  return date.toISOString().split('T')[0] as string;
});

onMounted(() => {
  store.fetchStatus();
  sinceDate.value = defaultDate.value;
});

onUnmounted(() => {
  store.disconnectWebSocket();
});

async function handleStartSync(): Promise<void> {
  const formattedDate = formatDateForApi(sinceDate.value);
  await store.startSync({
    since_date: formattedDate,
    dry_run: dryRun.value,
  });
}

function formatDateForApi(dateStr: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
  return `${date.getDate()}-${months[date.getMonth()]}-${date.getFullYear()}`;
}

function handleCancel(): void {
  store.cancelSync();
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    idle: '空闲',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  };
  return statusMap[status] || status;
}

function getStatusClass(status: string): string {
  const classMap: Record<string, string> = {
    idle: 'idle',
    running: 'running',
    completed: 'success',
    failed: 'error',
    cancelled: 'warning',
  };
  return classMap[status] || '';
}
</script>

<template>
  <div class="sync-view">
    <!-- Control Panel -->
    <div class="control-card">
      <h2 class="card-title">账单同步</h2>
      <p class="card-description">
        从邮箱获取信用卡电子账单，解析交易记录并同步到 Firefly III。
      </p>

      <div class="control-form">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">起始日期</label>
            <input
              v-model="sinceDate"
              type="date"
              class="form-input"
              :disabled="store.isRunning"
            />
          </div>

          <div class="form-group">
            <label class="form-label">预览模式</label>
            <label class="form-checkbox">
              <input
                v-model="dryRun"
                type="checkbox"
                :disabled="store.isRunning"
              />
              <span>仅解析不提交</span>
            </label>
          </div>
        </div>

        <div class="form-actions">
          <button
            v-if="!store.isRunning"
            class="btn btn-primary btn-lg"
            @click="handleStartSync"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" />
            </svg>
            开始同步
          </button>
          <button
            v-else
            class="btn btn-danger btn-lg"
            @click="handleCancel"
          >
            取消同步
          </button>
        </div>
      </div>
    </div>

    <!-- Status Panel -->
    <div class="status-card">
      <div class="status-header">
        <h3 class="status-title">同步状态</h3>
        <span class="status-badge" :class="getStatusClass(store.status)">
          {{ getStatusText(store.status) }}
        </span>
      </div>

      <!-- Progress -->
      <div v-if="store.isRunning" class="progress-section">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${store.progress}%` }"
          />
        </div>
        <div class="progress-info">
          <span>{{ store.progress }}%</span>
          <span v-if="store.currentAccount">
            正在处理: {{ store.currentAccount }}
          </span>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-value">{{ store.processedCount }}</span>
          <span class="stat-label">已处理</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ store.skippedCount }}</span>
          <span class="stat-label">已跳过</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ store.errorCount }}</span>
          <span class="stat-label">错误</span>
        </div>
      </div>
    </div>

    <!-- Log Panel -->
    <div class="log-card">
      <div class="log-header">
        <h3 class="log-title">同步日志</h3>
        <button
          class="btn btn-ghost btn-sm"
          @click="store.clearLogs"
        >
          清空
        </button>
      </div>
      <div class="log-content">
        <div v-if="store.logs.length === 0" class="log-empty">
          暂无日志
        </div>
        <div v-else class="log-list">
          <div
            v-for="(log, index) in store.logs"
            :key="index"
            class="log-item"
          >
            {{ log }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sync-view {
  padding: var(--space-6);
  max-width: var(--content-max-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Control Card */
.control-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.card-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.card-description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-6);
}

.control-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-row {
  display: flex;
  gap: var(--space-6);
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 200px;
}

.form-actions {
  display: flex;
  gap: var(--space-3);
}

/* Status Card */
.status-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.status-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.status-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.status-badge.idle {
  background: var(--color-background);
  color: var(--color-text-secondary);
}

.status-badge.running {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.status-badge.success {
  background: var(--color-success-light);
  color: var(--color-success);
}

.status-badge.error {
  background: var(--color-error-light);
  color: var(--color-error);
}

.status-badge.warning {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

/* Progress */
.progress-section {
  margin-bottom: var(--space-4);
}

.progress-bar {
  height: 8px;
  background: var(--color-background);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  transition: width var(--transition-base);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.stat-item {
  text-align: center;
  padding: var(--space-3);
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.stat-value {
  display: block;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Log Card */
.log-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.log-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  background: var(--color-surface-secondary);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
}

.log-empty {
  color: var(--color-text-tertiary);
  text-align: center;
  padding: var(--space-8);
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.log-item {
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

@media (max-width: 768px) {
  .sync-view {
    padding: var(--space-4);
  }

  .form-row {
    flex-direction: column;
    gap: var(--space-4);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
