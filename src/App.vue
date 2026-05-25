<template>
  <AppShell />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppShell from '@/components/layout/AppShell.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  userStore.initFromStorage()
})
</script>

<style lang="less">
/* Global reset */
html, body {
  height: 100%;
  width: 100%;
  overflow: hidden;
}
</style>
