<template>
  <div class="error-retry">
    <div class="error-retry__icon">{{ icon }}</div>
    <div class="error-retry__text">{{ text }}</div>
    <div v-if="actionText" class="error-retry__btn" @click="$emit('retry')">
      {{ actionText }}
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string
  text?: string
  actionText?: string
}>(), {
  icon: '⚠️',
  text: '加载失败，请检查网络连接',
  actionText: '重试',
})

defineEmits<{
  retry: []
}>()
</script>

<style lang="less" scoped>
.error-retry {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;

  &__icon {
    font-size: 36px;
    margin-bottom: 10px;
  }

  &__text {
    font-size: 13px;
    color: var(--text-secondary, #999);
    text-align: center;
    line-height: 1.5;
    margin-bottom: 14px;
  }

  &__btn {
    padding: 8px 24px;
    font-size: 14px;
    color: #fff;
    background: var(--primary-color, #4caf50);
    border-radius: 20px;
    cursor: pointer;
    font-weight: 500;
    transition: opacity 0.2s;

    &:active {
      opacity: 0.8;
    }
  }
}
</style>
