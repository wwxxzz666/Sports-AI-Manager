<template>
  <div class="bottom-nav safe-area-bottom">
    <router-link
      v-for="tab in tabs"
      :key="tab.path"
      :to="tab.path"
      class="bottom-nav__item"
      :class="{ 'bottom-nav__item--active': currentPath === tab.path }"
    >
      <div class="bottom-nav__icon">{{ tab.icon }}</div>
      <div class="bottom-nav__label">{{ tab.label }}</div>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentPath = computed(() => route.path)

const tabs = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/agents', label: '智能体', icon: '🤖' },
  { path: '/health', label: '健康', icon: '❤️' },
  { path: '/rating', label: '评级', icon: '🏆' },
]
</script>

<style lang="less" scoped>
.bottom-nav {
  display: flex;
  align-items: center;
  justify-content: space-around;
  height: 50px;
  background: var(--card-bg);
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    height: 100%;
    text-decoration: none;
    transition: color 0.2s;

    &--active {
      .bottom-nav__label {
        color: var(--primary-color);
        font-weight: 600;
      }
    }
  }

  &__icon {
    font-size: 22px;
    line-height: 1;
    margin-bottom: 2px;
  }

  &__label {
    font-size: 10px;
    color: var(--text-secondary);
    line-height: 1;
  }
}
</style>
