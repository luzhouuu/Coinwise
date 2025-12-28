<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budgets'
import { useI18nStore } from '@/stores/i18n'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import {
  MonthSelector,
  BudgetOverview,
  BudgetGoalCard,
  BudgetGoalModal,
  CategoryBreakdown,
  MonthComparison,
} from '@/components/spending-plan'
import type { BudgetSummaryItem } from '@/api/budgets'

const budgetStore = useBudgetStore()
const i18n = useI18nStore()

const showModal = ref(false)
const editingItem = ref<BudgetSummaryItem | null>(null)
const showDeleteConfirm = ref(false)
const deletingItem = ref<BudgetSummaryItem | null>(null)

onMounted(() => {
  budgetStore.fetchAll()
})

function handleAddGoal() {
  editingItem.value = null
  showModal.value = true
}

function handleEditGoal(item: BudgetSummaryItem) {
  editingItem.value = item
  showModal.value = true
}

function handleDeleteGoal(item: BudgetSummaryItem) {
  deletingItem.value = item
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  if (!deletingItem.value) return

  const budget = budgetStore.budgets.find(
    (b) => b.category_id === deletingItem.value!.category_id
  )
  if (budget) {
    await budgetStore.removeBudget(budget.id)
  }
  showDeleteConfirm.value = false
  deletingItem.value = null
}

function cancelDelete() {
  showDeleteConfirm.value = false
  deletingItem.value = null
}

async function handleCopyFromLastMonth() {
  const count = await budgetStore.copyFromPreviousMonth()
  if (count > 0) {
    // Could show a toast notification here
  }
}
</script>

<template>
  <div class="spending-plan-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">{{ i18n.t('budget.title') }}</h1>
        <MonthSelector />
      </div>
      <div class="header-actions">
        <button
          v-if="budgetStore.budgets.length === 0"
          class="btn btn-secondary"
          @click="handleCopyFromLastMonth"
        >
          {{ i18n.t('budget.copy_from_last') }}
        </button>
        <button class="btn btn-primary" @click="handleAddGoal">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          {{ i18n.t('budget.add_goal') }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="budgetStore.loading" class="loading-container">
      <LoadingSpinner />
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Overview Cards -->
      <BudgetOverview />

      <!-- Charts Section -->
      <div class="charts-section">
        <CategoryBreakdown />
        <MonthComparison />
      </div>

      <!-- Budget Goals List -->
      <div class="goals-section">
        <div class="section-header">
          <h2 class="section-title">{{ i18n.t('budget.goals') }}</h2>
        </div>

        <div v-if="budgetStore.summary && budgetStore.summary.items.length > 0" class="goals-list">
          <BudgetGoalCard
            v-for="item in budgetStore.summary.items"
            :key="item.category_id"
            :item="item"
            @edit="handleEditGoal"
            @delete="handleDeleteGoal"
          />
        </div>

        <EmptyState
          v-else
          :title="i18n.t('budget.no_budgets')"
          :description="i18n.t('budget.add_first')"
        >
          <template #action>
            <button class="btn btn-primary" @click="handleAddGoal">
              {{ i18n.t('budget.add_goal') }}
            </button>
          </template>
        </EmptyState>
      </div>
    </template>

    <!-- Add/Edit Modal -->
    <BudgetGoalModal
      :show="showModal"
      :edit-item="editingItem"
      @close="showModal = false"
      @saved="budgetStore.fetchAll()"
    />

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
        <div class="confirm-modal">
          <h3 class="confirm-title">{{ i18n.t('budget.delete_goal') }}</h3>
          <p class="confirm-message">{{ i18n.t('budget.delete_confirm') }}</p>
          <div class="confirm-actions">
            <button class="btn btn-secondary" @click="cancelDelete">
              {{ i18n.t('common.cancel') }}
            </button>
            <button class="btn btn-danger" @click="confirmDelete">
              {{ i18n.t('common.delete') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.spending-plan-view {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-6);
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  height: 40px;
  padding: 0 var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-primary:hover {
  background: var(--color-primary-hover);
}

.btn-secondary {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background: var(--color-surface-secondary);
}

.btn-danger {
  background: var(--color-error);
  color: var(--color-text-inverse);
}

.btn-danger:hover {
  background: #E53935;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}

@media (max-width: 1024px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

.goals-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Delete Confirmation Modal */
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
  z-index: var(--z-modal);
  padding: var(--space-4);
}

.confirm-modal {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--space-6);
  width: 100%;
  max-width: 360px;
  text-align: center;
}

.confirm-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-3);
}

.confirm-message {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-5);
}

.confirm-actions {
  display: flex;
  gap: var(--space-3);
}

.confirm-actions .btn {
  flex: 1;
}

@media (max-width: 768px) {
  .spending-plan-view {
    padding: var(--space-4);
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .header-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
