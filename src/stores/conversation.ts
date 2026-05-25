import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { generateId } from '@/utils/format'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  status: 'sending' | 'streaming' | 'complete' | 'error'
  attachments?: Attachment[]
  structured?: Record<string, unknown>
  createdAt: number
}

export interface Attachment {
  type: 'image' | 'video' | 'audio' | 'file'
  url: string
  name: string
}

export interface ConversationSession {
  id: string
  agentId: string
  title: string
  messages: Message[]
  createdAt: number
}

export const useConversationStore = defineStore('conversation', () => {
  const sessions = ref<Map<string, ConversationSession>>(new Map())
  const currentSessionId = ref<string>('')
  const isStreaming = ref(false)

  const currentSession = computed(() =>
    sessions.value.get(currentSessionId.value)
  )

  const messages = computed(() =>
    currentSession.value?.messages || []
  )

  function getOrCreateSession(agentId: string): string {
    const existing = Array.from(sessions.value.values()).find(
      (s) => s.agentId === agentId
    )
    if (existing) {
      currentSessionId.value = existing.id
      return existing.id
    }
    const session: ConversationSession = {
      id: generateId(),
      agentId,
      title: '',
      messages: [],
      createdAt: Date.now(),
    }
    sessions.value.set(session.id, session)
    currentSessionId.value = session.id
    return session.id
  }

  function switchSession(sessionId: string) {
    currentSessionId.value = sessionId
  }

  function addUserMessage(content: string, attachments?: Attachment[]): Message {
    const msg: Message = {
      id: generateId(),
      role: 'user',
      content,
      status: 'complete',
      attachments,
      createdAt: Date.now(),
    }
    const session = sessions.value.get(currentSessionId.value)
    if (session) {
      session.messages.push(msg)
      if (!session.title) {
        session.title = content.slice(0, 20)
      }
    }
    return msg
  }

  function addAssistantPlaceholder(): Message {
    const msg: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      status: 'streaming',
      createdAt: Date.now(),
    }
    const session = sessions.value.get(currentSessionId.value)
    if (session) {
      session.messages.push(msg)
    }
    isStreaming.value = true
    return msg
  }

  function updateStreamingMessage(messageId: string, chunk: string) {
    const session = sessions.value.get(currentSessionId.value)
    if (session) {
      const msg = session.messages.find((m) => m.id === messageId)
      if (msg) {
        msg.content += chunk
      }
    }
  }

  function completeStreamingMessage(messageId: string, fullContent: string, structured?: Record<string, unknown>) {
    const session = sessions.value.get(currentSessionId.value)
    if (session) {
      const msg = session.messages.find((m) => m.id === messageId)
      if (msg) {
        msg.content = fullContent
        msg.status = 'complete'
        if (structured) {
          msg.structured = structured
        }
      }
    }
    isStreaming.value = false
  }

  function setErrorStatus(messageId: string) {
    const session = sessions.value.get(currentSessionId.value)
    if (session) {
      const msg = session.messages.find((m) => m.id === messageId)
      if (msg) {
        msg.status = 'error'
        msg.content = msg.content || '抱歉，AI 服务暂时不可用，请稍后重试。'
      }
    }
    isStreaming.value = false
  }

  function getSessionList(agentId?: string): ConversationSession[] {
    const all = Array.from(sessions.value.values())
    if (agentId) {
      return all.filter((s) => s.agentId === agentId)
    }
    return all.sort((a, b) => b.createdAt - a.createdAt)
  }

  return {
    sessions,
    currentSessionId,
    currentSession,
    messages,
    isStreaming,
    getOrCreateSession,
    switchSession,
    addUserMessage,
    addAssistantPlaceholder,
    updateStreamingMessage,
    completeStreamingMessage,
    setErrorStatus,
    getSessionList,
  }
})
