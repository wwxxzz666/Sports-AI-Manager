import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AGENTS, type AgentConfig } from '@/utils/constants'

export const useAgentsStore = defineStore('agents', () => {
  const agents = ref<AgentConfig[]>(AGENTS)
  const activeAgentId = ref<string>('')
  const recentAgentIds = ref<string[]>([])

  const activeAgent = computed(() =>
    agents.value.find((a) => a.id === activeAgentId.value)
  )

  const recentAgents = computed(() =>
    recentAgentIds.value
      .map((id) => agents.value.find((a) => a.id === id))
      .filter(Boolean) as AgentConfig[]
  )

  const coreAgents = computed(() =>
    agents.value.filter((a) => a.group === 'core')
  )

  const healthAgents = computed(() =>
    agents.value.filter((a) => a.group === 'health')
  )

  const dataAgents = computed(() =>
    agents.value.filter((a) => a.group === 'data')
  )

  function activateAgent(agentId: string) {
    activeAgentId.value = agentId
    const idx = recentAgentIds.value.indexOf(agentId)
    if (idx !== -1) {
      recentAgentIds.value.splice(idx, 1)
    }
    recentAgentIds.value.unshift(agentId)
    if (recentAgentIds.value.length > 5) {
      recentAgentIds.value.pop()
    }
  }

  function getAgentById(agentId: string): AgentConfig | undefined {
    return agents.value.find((a) => a.id === agentId)
  }

  return {
    agents,
    activeAgentId,
    activeAgent,
    recentAgents,
    recentAgentIds,
    coreAgents,
    healthAgents,
    dataAgents,
    activateAgent,
    getAgentById,
  }
})
