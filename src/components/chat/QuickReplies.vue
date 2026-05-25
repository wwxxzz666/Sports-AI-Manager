<template>
  <div class="quick-replies">
    <div
      v-for="(question, index) in questions"
      :key="index"
      class="quick-replies__item"
      @click="$emit('select', question)"
    >
      {{ question }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  questions: string[]
}>()

defineEmits<{
  select: [question: string]
}>()
</script>

<style lang="less" scoped>
.quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 16px;

  &__item {
    padding: 6px 14px;
    border-radius: 16px;
    background: var(--primary-light);
    color: var(--primary-color);
    font-size: 13px;
    cursor: pointer;
    transition: background 0.2s;
    white-space: nowrap;

    &:active {
      background: #d0e8ff;
    }
  }
}
</style>
