<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budgets'
import { useStatisticsStore } from '@/stores/statistics'
import { useI18nStore } from '@/stores/i18n'
import type { BudgetSummaryItem } from '@/api/budgets'

interface Props {
  show: boolean
  editItem?: BudgetSummaryItem | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  saved: []
}>()

const budgetStore = useBudgetStore()
const statisticsStore = useStatisticsStore()
const i18n = useI18nStore()

const categoryId = ref<number | null>(null)
const amount = ref<number>(0)
const isRecurring = ref(true)
const saving = ref(false)

const isEdit = computed(() => !!props.editItem)

const title = computed(() =>
  isEdit.value ? i18n.t('budget.edit_goal') : i18n.t('budget.add_goal')
)

const availableCategories = computed(() => {
  if (isEdit.value) {
    return statisticsStore.categories
  }
  // Filter out categories that already have budgets
  const existingCategoryIds = budgetStore.budgets.map((b) => b.category_id)
  return statisticsStore.categories.filter(
    (c) => !existingCategoryIds.includes(Number(c.id))
  )
})

watch(
  () => props.show,
  (show) => {
    if (show) {
      if (props.editItem) {
        categoryId.value = props.editItem.category_id
        amount.value = props.editItem.budget_amount
      } else {
        categoryId.value = null
        amount.value = 0
        isRecurring.value = true
      }
    }
  }
)

onMounted(() => {
  if (statisticsStore.categories.length === 0) {
    statisticsStore.fetchCategories()
  }
})

async function handleSubmit() {
  if (!amount.value || amount.value <= 0) return
  if (!isEdit.value && !categoryId.value) return

  saving.value = true

  try {
    if (isEdit.value && props.editItem) {
      await budgetStore.editBudget(
        budgetStore.budgets.find((b) => b.category_id === props.editItem!.category_id)!.id,
        {
          amount: amount.value,
          is_recurring: isRecurring.value,
        }
      )
    } else {
      await budgetStore.addBudget({
        category_id: categoryId.value!,
        year: budgetStore.selectedMonth.year,
        month: budgetStore.selectedMonth.month,
        amount: amount.value,
        is_recurring: isRecurring.value,
      })
    }
    emit('saved')
    emit('close')
  } finally {
    saving.value = false
  }
}

function handleClose() {
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click.self="handleClose">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">{{ title }}</h2>
          <button class="close-btn" @click="handleClose">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <form class="modal-body" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label">{{ i18n.t('budget.select_category') }}</label>
            <select
              v-model="categoryId"
              class="form-select"
              :disabled="isEdit"
              required
            >
              <option :value="null" disabled>{{ i18n.t('budget.select_category') }}</option>
              <option
                v-for="cat in availableCategories"
                :key="cat.id"
                :value="Number(cat.id)"
              >
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">{{ i18n.t('budget.goal_amount') }}</label>
            <div class="input-with-prefix">
              <span class="input-prefix">{{ i18n.t('currency.symbol') }}</span>
              <input
                v-model.number="amount"
                type="number"
                class="form-input"
                min="0"
                step="0.01"
                required
              />
            </div>
          </div>

          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input
                v-model="isRecurring"
                type="checkbox"
                class="form-checkbox"
              />
              <span>{{ i18n.t('budget.is_recurring') }}</span>
            </label>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="handleClose">
              {{ i18n.t('common.cancel') }}
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="saving || !amount || (!isEdit && !categoryId)"
            >
              {{ saving ? i18n.t('common.loading') : i18n.t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
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

.modal-content {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: 100%;
  max-width: 400px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.form-select,
.form-input {
  height: 44px;
  padding: 0 var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast);
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-select:disabled {
  background: var(--color-surface-secondary);
  color: var(--color-text-tertiary);
}

.input-with-prefix {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.input-with-prefix:focus-within {
  border-color: var(--color-primary);
}

.input-prefix {
  padding: 0 var(--space-3);
  background: var(--color-surface-secondary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  height: 44px;
  display: flex;
  align-items: center;
}

.input-with-prefix .form-input {
  border: none;
  flex: 1;
}

.checkbox-group {
  flex-direction: row;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.form-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

.modal-actions {
  display: flex;
  gap: var(--space-3);
  padding-top: var(--space-4);
}

.btn {
  flex: 1;
  height: 44px;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background: var(--color-border-light);
}
</style>
