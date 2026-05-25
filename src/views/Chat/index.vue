<template>
  <div class="chat-page">
    <PageHeader
      :title="currentAgent?.name || '对话'"
      :show-back="true"
    />

    <div class="chat-page__agent-info" v-if="currentAgent">
      <div class="chat-page__agent-icon">{{ currentAgent.icon }}</div>
      <div class="chat-page__agent-desc">{{ currentAgent.description }}</div>
    </div>

    <!-- Quick Questions -->
    <QuickReplies
      v-if="conversationStore.messages.length === 0 && currentAgent"
      :questions="currentAgent.quickQuestions"
      @select="handleQuickQuestion"
    />

    <!-- Chat Messages -->
    <ChatStream
      :messages="conversationStore.messages"
      @retry="handleRetry"
    />

    <!-- Attachment Panel -->
    <AttachmentPanel
      v-model:show="showAttachPanel"
      @select="handleAttachSelect"
    />

    <!-- Input Bar -->
    <ChatInputBar
      ref="inputBarRef"
      :disabled="conversationStore.isStreaming"
      :placeholder="conversationStore.isStreaming ? 'AI 正在思考中...' : `问 ${currentAgent?.name || '助手'} 任何问题...`"
      @send="handleSend"
      @toggle-attach="showAttachPanel = true"
      @voice-input="handleVoiceInput"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAgentsStore } from '@/stores/agents'
import { useConversationStore } from '@/stores/conversation'
import { sendChatMessage } from '@/api/chat'
import PageHeader from '@/components/layout/PageHeader.vue'
import ChatStream from '@/components/chat/ChatStream.vue'
import ChatInputBar from '@/components/chat/ChatInputBar.vue'
import QuickReplies from '@/components/chat/QuickReplies.vue'
import AttachmentPanel from '@/components/chat/AttachmentPanel.vue'
import type { Message } from '@/stores/conversation'

const route = useRoute()
const agentsStore = useAgentsStore()
const conversationStore = useConversationStore()

const showAttachPanel = ref(false)
const inputBarRef = ref<InstanceType<typeof ChatInputBar>>()

const agentId = computed(() => route.params.agentId as string)
const currentAgent = computed(() => agentsStore.getAgentById(agentId.value))

onMounted(() => { initSession() })
watch(agentId, () => { initSession() })

function initSession() {
  if (agentId.value) {
    agentsStore.activateAgent(agentId.value)
    conversationStore.getOrCreateSession(agentId.value)
  }
}

function handleQuickQuestion(question: string) { handleSend(question) }

async function handleSend(text: string) {
  if (conversationStore.isStreaming) return

  conversationStore.addUserMessage(text)
  const assistantMsg = conversationStore.addAssistantPlaceholder()

  try {
    const res = await sendChatMessage(agentId.value, { message: text })
    conversationStore.completeStreamingMessage(assistantMsg.id, res.reply)
  } catch {
    conversationStore.setErrorStatus(assistantMsg.id)
  }
}

function handleRetry(message: Message) {
  const session = conversationStore.currentSession
  if (!session) return
  const idx = session.messages.findIndex((m) => m.id === message.id)
  if (idx !== -1) session.messages.splice(idx, 1)
  const lastUserMsg = [...session.messages].reverse().find((m) => m.role === 'user')
  if (lastUserMsg) handleSend(lastUserMsg.content)
}

function handleAttachSelect(type: string) {
  showAttachPanel.value = false
  if (type === 'camera' || type === 'image') {
    inputBarRef.value?.focus()
  } else if (type === 'video') {
    // Navigate to motion analysis
  }
}

function handleVoiceInput() { /* placeholder */ }
</script>

<style lang="less" scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-bg);

  &__agent-info {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: var(--card-bg);
    border-bottom: 1px solid var(--border-color);
  }

  &__agent-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: var(--app-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
  }

  &__agent-desc {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.4;
  }
}
</style>
