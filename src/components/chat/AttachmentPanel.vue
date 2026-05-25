<template>
  <van-popup
    :show="show"
    position="bottom"
    round
    :style="{ maxHeight: '60vh' }"
    @update:show="$emit('update:show', $event)"
  >
    <div class="attachment-panel">
      <div class="attachment-panel__title">选择附件</div>
      <div class="attachment-panel__grid">
        <div
          v-for="item in items"
          :key="item.type"
          class="attachment-panel__item"
          @click="$emit('select', item.type)"
        >
          <div class="attachment-panel__icon">{{ item.icon }}</div>
          <div class="attachment-panel__label">{{ item.label }}</div>
        </div>
      </div>
      <div class="attachment-panel__cancel" @click="$emit('update:show', false)">
        取消
      </div>
    </div>
  </van-popup>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
}>()

defineEmits<{
  'update:show': [value: boolean]
  select: [type: string]
}>()

const items = [
  { type: 'camera', icon: '📷', label: '拍照' },
  { type: 'image', icon: '🖼️', label: '图片' },
  { type: 'file', icon: '📄', label: '文件' },
  { type: 'video', icon: '🎬', label: '视频' },
]
</script>

<style lang="less" scoped>
.attachment-panel {
  padding: 16px;
  padding-bottom: calc(16px + var(--safe-area-bottom));

  &__title {
    font-size: 16px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 20px;
    color: var(--text-primary);
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 0 8px;
  }

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }

  &__icon {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    background: var(--app-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
  }

  &__label {
    font-size: 12px;
    color: var(--text-secondary);
  }

  &__cancel {
    text-align: center;
    margin-top: 20px;
    padding: 12px;
    font-size: 15px;
    color: var(--text-secondary);
    cursor: pointer;
    border-top: 1px solid var(--border-color);
  }
}
</style>
