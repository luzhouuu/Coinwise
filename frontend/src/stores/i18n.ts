/**
 * Internationalization store using Pinia Composition API.
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import zhMessages from '@/i18n/zh'
import enMessages from '@/i18n/en'

export type Locale = 'zh' | 'en'

const messages: Record<Locale, Record<string, string>> = {
  zh: zhMessages,
  en: enMessages,
}

export const useI18nStore = defineStore('i18n', () => {
  // State
  const locale = ref<Locale>('zh')

  // Computed
  const isZh = computed(() => locale.value === 'zh')
  const isEn = computed(() => locale.value === 'en')

  // Actions
  function t(key: string, params?: Record<string, string | number>): string {
    const message = messages[locale.value][key] || key

    if (!params) return message

    // Replace placeholders like {count} with actual values
    return Object.entries(params).reduce(
      (msg, [k, v]) => msg.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v)),
      message
    )
  }

  function setLocale(newLocale: Locale): void {
    locale.value = newLocale
    localStorage.setItem('locale', newLocale)
    document.documentElement.lang = newLocale
  }

  function toggleLocale(): void {
    setLocale(locale.value === 'zh' ? 'en' : 'zh')
  }

  function init(): void {
    const saved = localStorage.getItem('locale') as Locale | null
    if (saved && (saved === 'zh' || saved === 'en')) {
      locale.value = saved
    } else {
      // Detect browser language
      const browserLang = navigator.language.toLowerCase()
      locale.value = browserLang.startsWith('zh') ? 'zh' : 'en'
    }
    document.documentElement.lang = locale.value
  }

  // Format currency
  function formatCurrency(amount: number): string {
    const symbol = t('currency.symbol')
    const formatted = amount.toLocaleString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
    return `${symbol}${formatted}`
  }

  // Format month name
  function formatMonth(month: number): string {
    return t(`month.${month}`)
  }

  // Format date
  function formatDate(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date
    return d.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
      year: 'numeric',
      month: 'long',
    })
  }

  return {
    // State
    locale,
    // Computed
    isZh,
    isEn,
    // Actions
    t,
    setLocale,
    toggleLocale,
    init,
    formatCurrency,
    formatMonth,
    formatDate,
  }
})
