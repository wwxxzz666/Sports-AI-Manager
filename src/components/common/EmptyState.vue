<template>
  <div class="empty-state">
    <div class="empty-state__icon">{{ icon }}</div>
    <div class="empty-state__text">{{ text }}</div>
    <div v-if="actionText" class="empty-state__action" @click="$emit('action')">
      {{ actionText }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon?: string
  text: string
  actionText?: string
}>()

defineEmits<{
  action: []
}>()
</script>

<style lang="less" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;

  &__icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  &__text {
    font-size: 14px;
    color: var(--text-hint);
    text-align: center;
    line-height: 1.6;
  }

  &__action {
    margin-top: 16px;
    font-size: 14px;
    color: var(--primary-color);
    cursor: pointer;
  }
}
</style>
