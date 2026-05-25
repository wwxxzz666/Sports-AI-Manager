<template>
  <div class="loading-skeleton" :style="{ display: inline ? 'flex' : 'block' }">
    <div
      class="skeleton-block"
      :style="{
        width: width || '100%',
        height: height || '16px',
        borderRadius: rounded ? '50%' : '8px',
      }"
    ></div>
    <div
      v-if="lines > 1"
      class="skeleton-block"
      v-for="i in (lines - 1)"
      :key="i"
      :style="{
        width: (i === lines - 1 ? '60%' : '100%'),
        height: height || '16px',
        borderRadius: '8px',
        marginTop: '8px',
      }"
    ></div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  width?: string
  height?: string
  lines?: number
  rounded?: boolean
  inline?: boolean
}>(), {
  lines: 1,
  rounded: false,
  inline: false,
})
</script>

<style lang="less" scoped>
.loading-skeleton {
  padding: 12px 0;
}

.skeleton-block {
  background: linear-gradient(
    90deg,
    var(--card-bg, #f0f0f0) 25%,
    var(--border-color, #e0e0e0) 50%,
    var(--card-bg, #f0f0f0) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
