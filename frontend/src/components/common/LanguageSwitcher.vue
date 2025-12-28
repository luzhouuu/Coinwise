<script setup lang="ts">
import { useI18nStore } from '@/stores/i18n'

const i18n = useI18nStore()
</script>

<template>
  <button class="language-switcher" @click="i18n.toggleLocale">
    <span class="lang-option" :class="{ active: i18n.isEn }">EN</span>
    <span class="divider">|</span>
    <span class="lang-option" :class="{ active: i18n.isZh }">中文</span>
  </button>
</template>

<style scoped>
.language-switcher {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  height: 32px;
  padding: 0 var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.language-switcher:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.lang-option {
  color: var(--color-text-tertiary);
  transition: color var(--transition-fast);
}

.lang-option.active {
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}

.divider {
  color: var(--color-border);
}
</style>
