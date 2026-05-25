<template>
  <div class="page-header safe-area-top">
    <div class="page-header__left" @click="handleBack">
      <span v-if="showBack" class="page-header__back">‹</span>
    </div>
    <div class="page-header__title">{{ title }}</div>
    <div class="page-header__right">
      <slot name="right" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = defineProps<{
  title: string
  showBack?: boolean
}>()

const router = useRouter()

function handleBack() {
  if (props.showBack) {
    router.back()
  }
}
</script>

<style lang="less" scoped>
.page-header {
  display: flex;
  align-items: center;
  height: 44px;
  padding: 0 16px;
  padding-top: var(--safe-area-top);
  background: var(--card-bg);
  position: sticky;
  top: 0;
  z-index: 100;

  &__left {
    width: 40px;
    display: flex;
    align-items: center;
  }

  &__back {
    font-size: 28px;
    font-weight: 300;
    color: var(--text-primary);
    cursor: pointer;
    line-height: 1;
    margin-top: -2px;
  }

  &__title {
    flex: 1;
    text-align: center;
    font-size: 17px;
    font-weight: 600;
    color: var(--text-primary);
  }

  &__right {
    width: 40px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
  }
}
</style>
