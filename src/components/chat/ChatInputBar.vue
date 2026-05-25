<template>
  <div class="chat-input-bar">
    <div class="chat-input-bar__row">
      <div class="chat-input-bar__attach" @click="$emit('toggleAttach')">
        <span class="chat-input-bar__icon">📎</span>
      </div>
      <div class="chat-input-bar__input-wrap">
        <input
          ref="inputRef"
          v-model="inputText"
          class="chat-input-bar__input"
          type="text"
          :placeholder="placeholder"
          :disabled="disabled"
          @keyup.enter="handleSend"
        />
      </div>
      <div class="chat-input-bar__voice" @click="$emit('voiceInput')">
        <span class="chat-input-bar__icon">🎤</span>
      </div>
      <div
        class="chat-input-bar__send"
        :class="{ 'chat-input-bar__send--active': canSend }"
        @click="handleSend"
      >
        <span>发送</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  disabled?: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  send: [text: string]
  toggleAttach: []
  voiceInput: []
}>()

const inputRef = ref<HTMLInputElement>()
const inputText = ref('')

const canSend = computed(() => inputText.value.trim().length > 0 && !props.disabled)

function handleSend() {
  if (!canSend.value) return
  emit('send', inputText.value.trim())
  inputText.value = ''
}

function setInputText(text: string) {
  inputText.value = text
}

function focus() {
  inputRef.value?.focus()
}

defineExpose({ setInputText, focus })
</script>

<style lang="less" scoped>
.chat-input-bar {
  padding: 8px 12px;
  background: var(--card-bg);
  border-top: 1px solid var(--border-color);

  &__row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  &__attach,
  &__voice {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    flex-shrink: 0;
  }

  &__icon {
    font-size: 20px;
  }

  &__input-wrap {
    flex: 1;
    min-width: 0;
  }

  &__input {
    width: 100%;
    height: 36px;
    padding: 0 12px;
    border: 1px solid var(--border-color);
    border-radius: 18px;
    background: var(--app-bg);
    font-size: 14px;
    color: var(--text-primary);
    outline: none;
    transition: border-color 0.2s;

    &:focus {
      border-color: var(--primary-color);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  &__send {
    padding: 6px 16px;
    border-radius: 18px;
    background: var(--border-color);
    color: var(--text-hint);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    flex-shrink: 0;
    transition: all 0.2s;
    user-select: none;

    &--active {
      background: var(--primary-color);
      color: #fff;
    }
  }
}
</style>
