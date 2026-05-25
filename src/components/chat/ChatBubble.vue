<template>
  <div class="chat-bubble" :class="[`chat-bubble--${message.role}`, { 'chat-bubble--error': message.status === 'error' }]">
    <div v-if="message.role === 'assistant'" class="chat-bubble__avatar">
      <span class="chat-bubble__avatar-icon">🤖</span>
    </div>
    <div class="chat-bubble__body">
      <div class="chat-bubble__content">
        <div v-if="message.status === 'streaming' && !message.content" class="chat-bubble__typing">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
        <span v-else>{{ message.content }}</span>
      </div>
      <div v-if="message.status === 'error'" class="chat-bubble__retry" @click="$emit('retry', message)">
        发送失败，点击重试
      </div>
    </div>
    <div v-if="message.role === 'user'" class="chat-bubble__avatar chat-bubble__avatar--user">
      <span class="chat-bubble__avatar-icon">😊</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/stores/conversation'

defineProps<{
  message: Message
}>()

defineEmits<{
  retry: [message: Message]
}>()
</script>

<style lang="less" scoped>
.chat-bubble {
  display: flex;
  align-items: flex-start;
  padding: 8px 16px;
  gap: 8px;

  &--user {
    flex-direction: row-reverse;

    .chat-bubble__content {
      background: var(--primary-color);
      color: #fff;
      border-radius: 16px 4px 16px 16px;
    }
  }

  &--assistant {
    .chat-bubble__content {
      background: var(--card-bg);
      color: var(--text-primary);
      border-radius: 4px 16px 16px 16px;
    }
  }

  &__avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--primary-light);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    &--user {
      background: #fff3e0;
    }
  }

  &__avatar-icon {
    font-size: 18px;
  }

  &__body {
    max-width: 75%;
  }

  &__content {
    padding: 10px 14px;
    font-size: 14px;
    line-height: 1.6;
    word-break: break-word;
  }

  &__retry {
    font-size: 12px;
    color: var(--danger-color);
    margin-top: 4px;
    cursor: pointer;
  }

  &--error {
    .chat-bubble__content {
      background: #fff2f0;
      color: var(--danger-color);
    }
  }
}

.typing-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-hint);
  margin: 0 2px;
  animation: typing 1.4s infinite ease-in-out;

  &:nth-child(2) {
    animation-delay: 0.2s;
  }

  &:nth-child(3) {
    animation-delay: 0.4s;
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
