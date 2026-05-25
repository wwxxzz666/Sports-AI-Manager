<template>
  <div ref="streamRef" class="chat-stream">
    <EmptyState
      v-if="messages.length === 0"
      icon="💬"
      text="开始和 AI 助手对话吧"
    />
    <ChatBubble
      v-for="msg in messages"
      :key="msg.id"
      :message="msg"
      @retry="$emit('retry', msg)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { Message } from '@/stores/conversation'
import ChatBubble from './ChatBubble.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const props = defineProps<{
  messages: Message[]
}>()

defineEmits<{
  retry: [message: Message]
}>()

const streamRef = ref<HTMLElement>()

watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      if (streamRef.value) {
        streamRef.value.scrollTop = streamRef.value.scrollHeight
      }
    })
  }
)

watch(
  () => props.messages[props.messages.length - 1]?.content,
  () => {
    nextTick(() => {
      if (streamRef.value) {
        streamRef.value.scrollTop = streamRef.value.scrollHeight
      }
    })
  }
)
</script>

<style lang="less" scoped>
.chat-stream {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
  -webkit-overflow-scrolling: touch;
}
</style>
