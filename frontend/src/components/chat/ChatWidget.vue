<script setup lang="ts">
/**
 * Floating chat widget for bill assistant.
 */
import { ref, nextTick, onMounted, watch } from 'vue';
import { useChatStore } from '@/stores/chat';

const store = useChatStore();
const inputText = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

onMounted(() => {
  store.initChat();
});

// Auto scroll to bottom when new message arrives
watch(
  () => store.messages.length,
  async () => {
    await nextTick();
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  }
);

async function handleSend() {
  if (!inputText.value.trim() || store.loading) return;

  const message = inputText.value;
  inputText.value = '';
  await store.sendMessage(message);
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

// Format message with line breaks and markdown
function formatMessage(text: string): string {
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
}
</script>

<template>
  <div class="chat-widget">
    <!-- Floating Button -->
    <button
      v-if="!store.isOpen"
      class="chat-button"
      @click="store.openChat"
      title="打开智能助手"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path
          d="M12 2C6.48 2 2 6.48 2 12C2 13.85 2.5 15.55 3.35 17L2 22L7 20.65C8.45 21.5 10.15 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <circle cx="8" cy="12" r="1" fill="currentColor" />
        <circle cx="12" cy="12" r="1" fill="currentColor" />
        <circle cx="16" cy="12" r="1" fill="currentColor" />
      </svg>
    </button>

    <!-- Chat Window -->
    <Transition name="chat">
      <div v-if="store.isOpen" class="chat-window">
        <!-- Header -->
        <div class="chat-header">
          <div class="header-info">
            <div class="header-avatar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 2L2 7L12 12L22 7L12 2Z"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <path
                  d="M2 17L12 22L22 17"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <path
                  d="M2 12L12 17L22 12"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <span class="header-title">CoinWise 助手</span>
          </div>
          <button class="close-btn" @click="store.closeChat" title="关闭">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M18 6L6 18M6 6L18 18"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>

        <!-- Messages -->
        <div ref="messagesContainer" class="chat-messages">
          <div
            v-for="(msg, index) in store.messages"
            :key="index"
            class="message"
            :class="msg.role"
          >
            <div class="message-content">
              <span class="message-text" v-html="formatMessage(msg.content)" />
            </div>
          </div>

          <!-- Loading indicator -->
          <div v-if="store.loading" class="message assistant">
            <div class="message-content">
              <span class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </span>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="chat-input">
          <input
            v-model="inputText"
            type="text"
            placeholder="输入问题，如：餐饮花了多少？"
            @keydown="handleKeydown"
            :disabled="store.loading"
          />
          <button
            class="send-btn"
            @click="handleSend"
            :disabled="!inputText.trim() || store.loading"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

/* Floating Button */
.chat-button {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4);
  transition: all 0.3s ease;
}

.chat-button:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 122, 255, 0.5);
}

/* Chat Window */
.chat-window {
  width: 380px;
  height: 520px;
  background: var(--color-surface, white);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border, #e5e5e5);
}

/* Header */
.chat-header {
  padding: 16px;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-avatar {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title {
  font-weight: 600;
  font-size: 15px;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
}

.message.assistant {
  align-self: flex-start;
}

.message-content {
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
}

.message.user .message-content {
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background: var(--color-background, #f5f5f5);
  color: var(--color-text-primary, #333);
  border-bottom-left-radius: 4px;
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--color-text-tertiary, #999);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

/* Input */
.chat-input {
  padding: 12px 16px;
  border-top: 1px solid var(--color-border, #e5e5e5);
  display: flex;
  gap: 8px;
}

.chat-input input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--color-border, #e5e5e5);
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  background: var(--color-surface, white);
  color: var(--color-text-primary, #333);
}

.chat-input input:focus {
  border-color: #007AFF;
}

.chat-input input::placeholder {
  color: var(--color-text-tertiary, #999);
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  opacity: 0.9;
}

/* Transitions */
.chat-enter-active,
.chat-leave-active {
  transition: all 0.3s ease;
}

.chat-enter-from,
.chat-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

/* Mobile */
@media (max-width: 480px) {
  .chat-widget {
    bottom: 16px;
    right: 16px;
  }

  .chat-window {
    width: calc(100vw - 32px);
    height: calc(100vh - 100px);
    max-height: 600px;
  }
}
</style>
