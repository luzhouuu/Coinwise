/**
 * Chat store using Pinia Composition API.
 */

import { ref } from 'vue';
import { defineStore } from 'pinia';
import { sendMessage as sendChatMessage, type ChatMessage } from '@/api/chat';

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref<ChatMessage[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const isOpen = ref(false);

  // Actions
  function toggleChat() {
    isOpen.value = !isOpen.value;
  }

  function openChat() {
    isOpen.value = true;
  }

  function closeChat() {
    isOpen.value = false;
  }

  async function sendMessage(content: string): Promise<void> {
    if (!content.trim()) return;

    // Get history (exclude welcome message, limit to last 10 messages)
    const history = messages.value
      .slice(-10)
      .map(m => ({ role: m.role, content: m.content }));

    // Add user message
    messages.value.push({
      role: 'user',
      content: content.trim(),
    });

    loading.value = true;
    error.value = null;

    try {
      const response = await sendChatMessage(content, history);

      if (response.success) {
        // Add assistant message
        messages.value.push({
          role: 'assistant',
          content: response.reply,
        });
      } else {
        error.value = '发送失败，请重试';
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '发送失败，请重试';
      // Add error message
      messages.value.push({
        role: 'assistant',
        content: '抱歉，发生了错误，请稍后重试。',
      });
    } finally {
      loading.value = false;
    }
  }

  function clearMessages() {
    messages.value = [];
    error.value = null;
  }

  // Initialize with welcome message
  function initChat() {
    if (messages.value.length === 0) {
      messages.value.push({
        role: 'assistant',
        content: '你好！我是 CoinWise 智能助手，可以帮你查询账单数据。\n\n试试问我：\n• 餐饮花了多少钱？\n• 最大的一笔支出是什么？\n• 上个月总共花了多少？',
      });
    }
  }

  return {
    // State
    messages,
    loading,
    error,
    isOpen,
    // Actions
    toggleChat,
    openChat,
    closeChat,
    sendMessage,
    clearMessages,
    initChat,
  };
});
