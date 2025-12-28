<script setup lang="ts">
/**
 * Configuration management view.
 */
import { onMounted, ref, reactive } from 'vue';
import { useConfigStore } from '@/stores/config';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import type { EmailAccountCreate } from '@/api/config';

const store = useConfigStore();

const activeTab = ref<'email' | 'category'>('email');

// Email form
const showEmailModal = ref(false);
const newEmailAccount = reactive<EmailAccountCreate>({
  email: '',
  password: '',
  imap_server: '',
  imap_port: 993,
  bank_type: 'cmb',
});

// Bank type options
const bankTypes = [
  { value: 'cmb', label: '招商银行' },
  { value: 'ccb', label: '建设银行' },
  { value: 'abc', label: '农业银行' },
];

onMounted(() => {
  store.fetchAll();
});

// Tab switching
function setTab(tab: 'email' | 'category'): void {
  activeTab.value = tab;
}

// Email actions
function openEmailModal(): void {
  newEmailAccount.email = '';
  newEmailAccount.password = '';
  newEmailAccount.imap_server = '';
  newEmailAccount.imap_port = 993;
  newEmailAccount.bank_type = 'cmb';
  showEmailModal.value = true;
}

function closeEmailModal(): void {
  showEmailModal.value = false;
}

async function handleAddEmail(): Promise<void> {
  if (!newEmailAccount.email || !newEmailAccount.password || !newEmailAccount.imap_server) {
    alert('请填写完整信息');
    return;
  }

  const success = await store.addEmailAccount({
    ...newEmailAccount,
  });

  if (success) {
    closeEmailModal();
  }
}

async function handleDeleteEmail(id: number): Promise<void> {
  if (confirm('确定要删除这个邮箱账户吗？')) {
    await store.deleteEmailAccount(id);
  }
}

// Get bank name
function getBankName(bankType: string): string {
  const bank = bankTypes.find(b => b.value === bankType);
  return bank?.label || bankType;
}
</script>

<template>
  <div class="config-view">
    <!-- Tabs -->
    <div class="tabs-container">
      <div class="tabs">
        <button
          class="tab"
          :class="{ active: activeTab === 'email' }"
          @click="setTab('email')"
        >
          邮箱账户
        </button>
        <button
          class="tab"
          :class="{ active: activeTab === 'category' }"
          @click="setTab('category')"
        >
          分类管理
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="loading-container">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Tab Content -->
    <div v-else class="tab-content">
      <!-- Email Accounts -->
      <div v-if="activeTab === 'email'" class="config-section">
        <div class="section-header">
          <h2 class="section-title">邮箱账户管理</h2>
          <button class="btn btn-primary" @click="openEmailModal">
            添加邮箱
          </button>
        </div>

        <div class="section-card">
          <div v-if="store.emailAccounts.length === 0" class="empty-message">
            还没有配置任何邮箱账户，点击"添加邮箱"开始配置
          </div>
          <div v-else class="account-list">
            <div
              v-for="account in store.emailAccounts"
              :key="account.id"
              class="account-item"
            >
              <div class="account-info">
                <span class="account-email">{{ account.email }}</span>
                <div class="account-meta">
                  <span class="account-bank badge">{{ getBankName(account.bank_type) }}</span>
                  <span class="account-server">{{ account.imap_server }}:{{ account.imap_port }}</span>
                  <span
                    class="account-status"
                    :class="{ active: account.is_active }"
                  >
                    {{ account.is_active ? '启用' : '禁用' }}
                  </span>
                </div>
              </div>
              <div class="account-actions">
                <button
                  class="btn btn-ghost btn-sm text-error"
                  @click="handleDeleteEmail(account.id)"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Categories -->
      <div v-if="activeTab === 'category'" class="config-section">
        <div class="section-header">
          <h2 class="section-title">分类管理</h2>
        </div>

        <div class="section-card">
          <div class="categories-grid">
            <div
              v-for="cat in store.categories"
              :key="cat.id"
              class="category-item"
            >
              <div
                class="category-color"
                :style="{ backgroundColor: cat.color || '#8E8E93' }"
              ></div>
              <span class="category-name">{{ cat.name }}</span>
            </div>
          </div>
        </div>

        <div v-if="store.categoryRules.length > 0" class="section-card">
          <h3 class="subsection-title">自动分类规则</h3>
          <div class="rules-list">
            <div
              v-for="rule in store.categoryRules"
              :key="rule.id"
              class="rule-item"
            >
              <span class="rule-pattern">{{ rule.pattern }}</span>
              <span class="rule-arrow">-></span>
              <span class="rule-category badge">{{ rule.category_name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Email Modal -->
    <div v-if="showEmailModal" class="modal-overlay" @click.self="closeEmailModal">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">添加邮箱账户</h2>
          <button class="modal-close" @click="closeEmailModal">&times;</button>
        </div>
        <form class="modal-body" @submit.prevent="handleAddEmail">
          <div class="form-group">
            <label class="form-label">银行类型</label>
            <select
              v-model="newEmailAccount.bank_type"
              class="form-input form-select"
              required
            >
              <option
                v-for="bank in bankTypes"
                :key="bank.value"
                :value="bank.value"
              >
                {{ bank.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">邮箱地址</label>
            <input
              v-model="newEmailAccount.email"
              type="email"
              class="form-input"
              placeholder="your@email.com"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">IMAP 密码/授权码</label>
            <input
              v-model="newEmailAccount.password"
              type="password"
              class="form-input"
              placeholder="邮箱授权码"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">IMAP 服务器</label>
            <input
              v-model="newEmailAccount.imap_server"
              type="text"
              class="form-input"
              placeholder="imap.example.com"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">IMAP 端口</label>
            <input
              v-model.number="newEmailAccount.imap_port"
              type="number"
              class="form-input"
              placeholder="993"
              required
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeEmailModal">
              取消
            </button>
            <button type="submit" class="btn btn-primary">
              保存
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.config-view {
  padding: var(--space-6);
  max-width: var(--content-max-width);
  margin: 0 auto;
}

/* Tabs */
.tabs-container {
  margin-bottom: var(--space-6);
}

.tabs {
  display: flex;
  gap: var(--space-1);
  background: var(--color-surface);
  padding: var(--space-1);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.tab {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.tab:hover {
  color: var(--color-text-primary);
}

.tab.active {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

/* Loading */
.loading-container {
  display: flex;
  justify-content: center;
  padding: var(--space-12);
}

/* Section */
.config-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.subsection-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.section-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.empty-message {
  color: var(--color-text-tertiary);
  text-align: center;
  padding: var(--space-6);
}

/* Account List */
.account-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.account-email {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.account-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--font-size-sm);
}

.account-bank {
  background: var(--color-primary);
  color: white;
}

.account-server {
  color: var(--color-text-tertiary);
  font-family: var(--font-family-mono);
}

.account-status {
  color: var(--color-text-tertiary);
}

.account-status.active {
  color: var(--color-success);
}

.account-actions {
  display: flex;
  gap: var(--space-2);
}

/* Categories Grid */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-3);
}

.category-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.category-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.category-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

/* Rules List */
.rules-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.rule-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--color-background);
  border-radius: var(--radius-md);
}

.rule-pattern {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.rule-arrow {
  color: var(--color-text-tertiary);
}

.rule-category {
  background: var(--color-secondary);
  color: var(--color-text-primary);
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.text-error {
  color: var(--color-error) !important;
}

@media (max-width: 768px) {
  .config-view {
    padding: var(--space-4);
  }

  .tabs {
    flex-direction: column;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
  }

  .account-item {
    flex-direction: column;
    gap: var(--space-3);
    align-items: flex-start;
  }

  .modal {
    margin: var(--space-4);
    max-height: calc(100vh - var(--space-8));
  }
}
</style>
