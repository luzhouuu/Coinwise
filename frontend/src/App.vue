<script setup lang="ts">
/**
 * Root application component with layout.
 */
import { ref } from 'vue';
import AppHeader from '@/components/common/AppHeader.vue';
import AppSidebar from '@/components/common/AppSidebar.vue';

const sidebarOpen = ref(false);

function toggleSidebar(): void {
  sidebarOpen.value = !sidebarOpen.value;
}

function closeSidebar(): void {
  sidebarOpen.value = false;
}
</script>

<template>
  <div class="app-layout">
    <AppSidebar :open="sidebarOpen" @close="closeSidebar" />

    <div class="app-main">
      <AppHeader :sidebar-open="sidebarOpen" @toggle-sidebar="toggleSidebar" />

      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
}

.app-main {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-content {
  flex: 1;
  background: var(--color-background);
}

@media (max-width: 768px) {
  .app-main {
    margin-left: 0;
  }
}
</style>
