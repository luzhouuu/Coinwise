<script setup lang="ts">
/**
 * Login page view.
 */
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const showPassword = ref(false);

onMounted(async () => {
  // Redirect if already authenticated
  if (await authStore.checkAuth()) {
    router.push('/dashboard');
  }
});

async function handleSubmit(): Promise<void> {
  if (!username.value || !password.value) {
    return;
  }

  const success = await authStore.login(username.value, password.value);
  if (success) {
    const redirect = router.currentRoute.value.query.redirect as string;
    router.push(redirect || '/dashboard');
  }
}
</script>

<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-header">
        <div class="login-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
          </svg>
        </div>
        <h1 class="login-title">CoinWise</h1>
        <p class="login-subtitle">智能家庭支出管理</p>
      </div>

      <form class="login-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label" for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="form-input"
            placeholder="请输入用户名"
            autocomplete="username"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="password">密码</label>
          <div class="password-input-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="请输入密码"
              autocomplete="current-password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="authStore.loading || !username || !password"
        >
          <span v-if="authStore.loading" class="loading-spinner"></span>
          <span v-else>登录</span>
        </button>
      </form>

      <div class="login-footer">
        <p>安全登录 · 数据加密传输</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 100%);
  padding: var(--space-4);
}

.login-container {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  border-radius: var(--radius-2xl);
  padding: var(--space-10);
  border: 1px solid var(--color-border);
}

.login-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.login-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--space-4);
  background: var(--color-primary);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.login-logo svg {
  width: 36px;
  height: 36px;
}

.login-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
  letter-spacing: var(--letter-spacing-tight);
}

.login-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.form-input::placeholder {
  color: var(--color-text-tertiary);
}

.password-input-wrapper {
  position: relative;
}

.password-input-wrapper .form-input {
  padding-right: 70px;
}

.password-toggle {
  position: absolute;
  right: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-xs);
  transition: color var(--transition-fast);
}

.password-toggle:hover {
  color: var(--color-primary);
}

.error-message {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  text-align: center;
  padding: var(--space-3);
  background: var(--color-error-light);
  border-radius: var(--radius-md);
}

.login-button {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-inverse);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.login-button:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.login-button:active:not(:disabled) {
  transform: scale(0.98);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.login-footer {
  margin-top: var(--space-8);
  text-align: center;
}

.login-footer p {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

@media (max-width: 480px) {
  .login-container {
    padding: var(--space-6);
    border-radius: var(--radius-xl);
  }
}
</style>
