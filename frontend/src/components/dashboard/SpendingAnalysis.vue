<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getMonthlyAnalysis, type AnalysisResponse } from '@/api/analysis'
import { useI18nStore } from '@/stores/i18n'

const i18n = useI18nStore()
const loading = ref(false)
const error = ref<string | null>(null)
const analysis = ref<AnalysisResponse | null>(null)

// Simple markdown to HTML converter
function parseMarkdown(text: string): string {
  return text
    // Bold: **text** or __text__
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    // Italic: *text* or _text_
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/_([^_]+)_/g, '<em>$1</em>')
    // Headers
    .replace(/^### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^## (.*$)/gm, '<h3>$1</h3>')
    .replace(/^# (.*$)/gm, '<h2>$1</h2>')
    // Unordered lists
    .replace(/^\s*[-*]\s+(.*)$/gm, '<li>$1</li>')
    // Numbered lists
    .replace(/^\s*\d+\.\s+(.*)$/gm, '<li>$1</li>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    // Wrap in paragraph
    .replace(/^(.*)$/, '<p>$1</p>')
    // Clean up list items
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/<\/ul>\s*<ul>/g, '')
}

const analysisHtml = computed(() => {
  if (!analysis.value?.analysis) return ''
  return parseMarkdown(analysis.value.analysis)
})

async function fetchAnalysis() {
  loading.value = true
  error.value = null

  try {
    // Don't pass year/month to let backend auto-detect latest month with data
    analysis.value = await getMonthlyAnalysis()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '分析请求失败'
  } finally {
    loading.value = false
  }
}

async function refresh() {
  await fetchAnalysis()
}

onMounted(() => {
  fetchAnalysis()
})
</script>

<template>
  <div class="analysis-card">
    <div class="card-header">
      <div class="header-left">
        <svg class="ai-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        <h3 class="card-title">{{ i18n.isZh ? 'AI 支出分析' : 'AI Spending Analysis' }}</h3>
      </div>
      <button class="refresh-btn" @click="refresh" :disabled="loading">
        <svg
          :class="{ spinning: loading }"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
        >
          <path
            d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </div>

    <div class="card-body">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <span>{{ i18n.isZh ? '正在分析...' : 'Analyzing...' }}</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <span>{{ error }}</span>
        <button class="retry-btn" @click="refresh">{{ i18n.isZh ? '重试' : 'Retry' }}</button>
      </div>

      <!-- Analysis Content -->
      <div v-else-if="analysis" class="analysis-content">
        <div class="period-badge">{{ analysis.period }}</div>
        <div class="analysis-text" v-html="analysisHtml"></div>

        <div v-if="analysis.top_categories.length > 0" class="category-summary">
          <div
            v-for="cat in analysis.top_categories.slice(0, 3)"
            :key="cat.name"
            class="category-chip"
          >
            <span class="cat-name">{{ cat.name }}</span>
            <span class="cat-amount">¥{{ cat.amount.toLocaleString() }}</span>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <span>{{ i18n.isZh ? '暂无分析数据' : 'No analysis available' }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analysis-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  color: white;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.ai-icon {
  opacity: 0.9;
}

.card-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.refresh-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn svg.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.card-body {
  min-height: 100px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-6) 0;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) 0;
}

.retry-btn {
  padding: var(--space-2) var(--space-4);
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-md);
  color: white;
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.retry-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.period-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  width: fit-content;
}

.analysis-text {
  font-size: var(--font-size-sm);
  line-height: 1.7;
  opacity: 0.95;
}

.analysis-text :deep(p) {
  margin: 0 0 var(--space-2) 0;
}

.analysis-text :deep(h2),
.analysis-text :deep(h3),
.analysis-text :deep(h4) {
  margin: var(--space-3) 0 var(--space-2) 0;
  font-weight: var(--font-weight-semibold);
}

.analysis-text :deep(h2) { font-size: var(--font-size-md); }
.analysis-text :deep(h3) { font-size: var(--font-size-base); }
.analysis-text :deep(h4) { font-size: var(--font-size-sm); }

.analysis-text :deep(ul) {
  margin: var(--space-2) 0;
  padding-left: var(--space-4);
  list-style: disc;
}

.analysis-text :deep(li) {
  margin: var(--space-1) 0;
}

.analysis-text :deep(strong) {
  font-weight: var(--font-weight-semibold);
}

.analysis-text :deep(em) {
  font-style: italic;
}

.category-summary {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.category-chip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
}

.cat-name {
  opacity: 0.8;
}

.cat-amount {
  font-weight: var(--font-weight-medium);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6) 0;
  opacity: 0.7;
}
</style>
