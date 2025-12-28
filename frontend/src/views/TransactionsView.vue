<script setup lang="ts">
/**
 * Transactions list view with filtering, pagination, and manual entry.
 */
import { onMounted, ref, reactive } from 'vue';
import { useTransactionStore } from '@/stores/transactions';
import { useConfigStore } from '@/stores/config';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import EmptyState from '@/components/common/EmptyState.vue';
import type { TransactionCreate } from '@/api/transactions';

const transactionStore = useTransactionStore();
const configStore = useConfigStore();

const searchQuery = ref('');
const selectedCategoryId = ref<number | undefined>();
const startDate = ref('');
const endDate = ref('');
const showAddModal = ref(false);
const isSubmitting = ref(false);

const newTransaction = reactive<TransactionCreate>({
  transaction_date: new Date().toISOString().slice(0, 16),
  amount: 0,
  description: '',
  category_id: null,
  transaction_type: 'withdrawal',
  source_account: '',
  notes: '',
  tags: [],
});

onMounted(() => {
  transactionStore.fetchTransactions();
  configStore.fetchCategories();
});

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
  }).format(value);
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

function handleSearch(): void {
  transactionStore.setFilter('search', searchQuery.value);
}

function handleCategoryChange(): void {
  transactionStore.setFilter('category_id', selectedCategoryId.value);
}

function handleDateChange(): void {
  if (startDate.value) {
    transactionStore.setFilter('start_date', startDate.value);
  }
  if (endDate.value) {
    transactionStore.setFilter('end_date', endDate.value);
  }
}

function handlePageChange(page: number): void {
  transactionStore.setPage(page);
}

function resetFilters(): void {
  searchQuery.value = '';
  selectedCategoryId.value = undefined;
  startDate.value = '';
  endDate.value = '';
  transactionStore.resetFilters();
}

async function handleDelete(id: number): Promise<void> {
  if (confirm('确定要删除这条交易记录吗？')) {
    await transactionStore.deleteTransaction(id);
  }
}

function openAddModal(): void {
  // Reset form
  newTransaction.transaction_date = new Date().toISOString().slice(0, 16);
  newTransaction.amount = 0;
  newTransaction.description = '';
  newTransaction.category_id = null;
  newTransaction.transaction_type = 'withdrawal';
  newTransaction.source_account = '';
  newTransaction.notes = '';
  newTransaction.tags = [];
  showAddModal.value = true;
}

function closeAddModal(): void {
  showAddModal.value = false;
}

async function handleSubmit(): Promise<void> {
  if (!newTransaction.description || newTransaction.amount <= 0) {
    alert('请填写描述和金额');
    return;
  }

  isSubmitting.value = true;
  try {
    const result = await transactionStore.createTransaction({
      ...newTransaction,
      transaction_date: new Date(newTransaction.transaction_date).toISOString(),
    });
    if (result) {
      closeAddModal();
    }
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="transactions-view">
    <!-- Header with Add Button -->
    <div class="view-header">
      <h1 class="view-title">交易记录</h1>
      <button class="btn btn-primary" @click="openAddModal">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
          <path d="M8 2a.5.5 0 01.5.5v5h5a.5.5 0 010 1h-5v5a.5.5 0 01-1 0v-5h-5a.5.5 0 010-1h5v-5A.5.5 0 018 2z"/>
        </svg>
        手动录入
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-card">
      <div class="filters-row">
        <div class="filter-group search">
          <input
            v-model="searchQuery"
            type="text"
            class="form-input"
            placeholder="搜索交易描述..."
            @keyup.enter="handleSearch"
          />
          <button class="btn btn-primary btn-sm" @click="handleSearch">
            搜索
          </button>
        </div>

        <div class="filter-group">
          <select
            v-model="selectedCategoryId"
            class="form-input form-select"
            @change="handleCategoryChange"
          >
            <option :value="undefined">全部分类</option>
            <option
              v-for="cat in configStore.categories"
              :key="cat.id"
              :value="cat.id"
            >
              {{ cat.name }}
            </option>
          </select>
        </div>

        <div class="filter-group dates">
          <input
            v-model="startDate"
            type="date"
            class="form-input"
            @change="handleDateChange"
          />
          <span class="date-separator">至</span>
          <input
            v-model="endDate"
            type="date"
            class="form-input"
            @change="handleDateChange"
          />
        </div>

        <button class="btn btn-ghost btn-sm" @click="resetFilters">
          重置
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="transactionStore.loading" class="loading-container">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Empty State -->
    <div v-else-if="transactionStore.transactions.length === 0" class="empty-container">
      <EmptyState
        title="暂无交易记录"
        description="点击【手动录入】添加交易，或通过邮件同步"
        icon="folder"
      />
    </div>

    <!-- Transaction List -->
    <div v-else class="transactions-list">
      <div
        v-for="tx in transactionStore.transactions"
        :key="tx.id"
        class="transaction-card"
      >
        <div class="tx-main">
          <div class="tx-info">
            <span class="tx-description">{{ tx.description }}</span>
            <div class="tx-meta">
              <span class="tx-date">{{ formatDate(tx.transaction_date) }}</span>
              <span v-if="tx.category_name" class="tx-category badge">
                {{ tx.category_name }}
              </span>
              <span v-if="tx.is_manual" class="tx-manual badge badge-info">
                手动
              </span>
            </div>
          </div>
          <div class="tx-amount" :class="tx.transaction_type">
            {{ tx.transaction_type === 'deposit' ? '+' : '-' }}{{ formatCurrency(tx.amount) }}
          </div>
        </div>
        <button
          class="tx-delete btn btn-ghost btn-sm"
          title="删除"
          @click="handleDelete(tx.id)"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M5.5 5.5A.5.5 0 016 6v6a.5.5 0 01-1 0V6a.5.5 0 01.5-.5zm2.5 0a.5.5 0 01.5.5v6a.5.5 0 01-1 0V6a.5.5 0 01.5-.5zm3 .5a.5.5 0 00-1 0v6a.5.5 0 001 0V6z" />
            <path fill-rule="evenodd" d="M14.5 3a1 1 0 01-1 1H13v9a2 2 0 01-2 2H5a2 2 0 01-2-2V4h-.5a1 1 0 01-1-1V2a1 1 0 011-1H6a1 1 0 011-1h2a1 1 0 011 1h3.5a1 1 0 011 1v1zM4.118 4L4 4.059V13a1 1 0 001 1h6a1 1 0 001-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" />
          </svg>
        </button>
      </div>

      <!-- Pagination -->
      <div class="pagination">
        <button
          class="btn btn-secondary btn-sm"
          :disabled="transactionStore.pagination.page <= 1"
          @click="handlePageChange(transactionStore.pagination.page - 1)"
        >
          上一页
        </button>
        <span class="pagination-info">
          第 {{ transactionStore.pagination.page }} / {{ transactionStore.totalPages }} 页
          (共 {{ transactionStore.pagination.total }} 条)
        </span>
        <button
          class="btn btn-secondary btn-sm"
          :disabled="!transactionStore.hasMore"
          @click="handlePageChange(transactionStore.pagination.page + 1)"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- Add Transaction Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">手动录入交易</h2>
          <button class="modal-close" @click="closeAddModal">&times;</button>
        </div>
        <form class="modal-body" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label">交易类型</label>
            <div class="radio-group">
              <label class="radio-label">
                <input
                  v-model="newTransaction.transaction_type"
                  type="radio"
                  value="withdrawal"
                />
                支出
              </label>
              <label class="radio-label">
                <input
                  v-model="newTransaction.transaction_type"
                  type="radio"
                  value="deposit"
                />
                收入
              </label>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">日期时间</label>
            <input
              v-model="newTransaction.transaction_date"
              type="datetime-local"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">金额</label>
            <input
              v-model.number="newTransaction.amount"
              type="number"
              step="0.01"
              min="0"
              class="form-input"
              placeholder="0.00"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">描述</label>
            <input
              v-model="newTransaction.description"
              type="text"
              class="form-input"
              placeholder="交易描述"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">分类</label>
            <select
              v-model="newTransaction.category_id"
              class="form-input form-select"
            >
              <option :value="null">未分类</option>
              <option
                v-for="cat in configStore.categories"
                :key="cat.id"
                :value="cat.id"
              >
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">来源账户</label>
            <input
              v-model="newTransaction.source_account"
              type="text"
              class="form-input"
              placeholder="如：招商银行信用卡"
            />
          </div>

          <div class="form-group">
            <label class="form-label">备注</label>
            <textarea
              v-model="newTransaction.notes"
              class="form-input"
              rows="2"
              placeholder="可选备注"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeAddModal">
              取消
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.transactions-view {
  padding: var(--space-6);
  max-width: var(--content-max-width);
  margin: 0 auto;
}

/* Header */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.view-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.view-header .btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

/* Filters */
.filters-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
  box-shadow: var(--shadow-sm);
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
}

.filter-group {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.filter-group.search {
  flex: 1;
  min-width: 200px;
}

.filter-group.search .form-input {
  flex: 1;
}

.filter-group.dates {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.date-separator {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

/* Loading & Empty */
.loading-container,
.empty-container {
  display: flex;
  justify-content: center;
  padding: var(--space-12);
}

/* Transaction List */
.transactions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.transaction-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  box-shadow: var(--shadow-xs);
  transition: box-shadow var(--transition-fast);
}

.transaction-card:hover {
  box-shadow: var(--shadow-sm);
}

.tx-main {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
}

.tx-info {
  flex: 1;
  min-width: 0;
}

.tx-description {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tx-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-1);
}

.tx-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.tx-category {
  font-size: var(--font-size-xs);
}

.tx-manual {
  font-size: var(--font-size-xs);
}

.badge-info {
  background: var(--color-primary);
  color: white;
}

.tx-amount {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  white-space: nowrap;
}

.tx-amount.withdrawal {
  color: var(--color-error);
}

.tx-amount.deposit {
  color: var(--color-success);
}

.tx-delete {
  opacity: 0;
  transition: opacity var(--transition-fast);
  color: var(--color-text-tertiary);
}

.transaction-card:hover .tx-delete {
  opacity: 1;
}

.tx-delete:hover {
  color: var(--color-error);
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-4);
  margin-top: var(--space-6);
  padding: var(--space-4);
}

.pagination-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.modal-close {
  font-size: 24px;
  color: var(--color-text-tertiary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-close:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-6);
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}

.radio-group {
  display: flex;
  gap: var(--space-4);
}

.radio-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

@media (max-width: 768px) {
  .transactions-view {
    padding: var(--space-4);
  }

  .view-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
  }

  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    width: 100%;
  }

  .filter-group.search {
    min-width: unset;
  }

  .tx-main {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
  }

  .tx-amount {
    align-self: flex-end;
  }

  .modal {
    margin: var(--space-4);
    max-height: calc(100vh - var(--space-8));
  }
}
</style>
