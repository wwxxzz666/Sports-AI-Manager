import apiClient from './client'

export interface ChatRequest {
  conversation_id?: string
  message: string
  attachments?: string[]
  metadata?: Record<string, unknown>
}

export interface ChatResponse {
  conversation_id: string
  reply: string
  structured?: Record<string, unknown>
  message_id: string
}

export interface ConversationInfo {
  id: string
  agent_type: string
  title: string
  created_at: string
}

export function sendChatMessage(agentType: string, data: ChatRequest): Promise<ChatResponse> {
  return apiClient.post(`/agents/${agentType}/chat`, data)
}

export function getConversationHistory(agentType: string): Promise<ConversationInfo[]> {
  return apiClient.get(`/agents/${agentType}/history`)
}

export function deleteConversation(agentType: string, conversationId: string): Promise<void> {
  return apiClient.delete(`/agents/${agentType}/history/${conversationId}`)
}
