<template>
  <div class="app-shell">
    <div class="app-shell__content">
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </div>
    <BottomNav v-if="showTabBar" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BottomNav from './BottomNav.vue'

const route = useRoute()
const showTabBar = computed(() => route.meta.showTabBar !== false)
</script>

<style lang="less" scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-bg);

  &__content {
    flex: 1;
    overflow: hidden;
    position: relative;
  }
}
</style>
