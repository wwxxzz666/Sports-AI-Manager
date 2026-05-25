<template>
  <div class="agents-page">
    <div class="agents-page__search">
      <van-search
        v-model="searchText"
        placeholder="搜索智能体"
        shape="round"
      />
    </div>

    <div class="agents-page__content">
      <div
        v-for="(groupAgents, groupKey) in filteredGroups"
        :key="groupKey"
        class="agent-group"
      >
        <div class="agent-group__title">{{ groupNames[groupKey] }}</div>
        <div class="agent-group__grid">
          <div
            v-for="agent in groupAgents"
            :key="agent.id"
            class="agent-card"
            @click="goToAgent(agent.id)"
          >
            <div class="agent-card__icon">{{ agent.icon }}</div>
            <div class="agent-card__info">
              <div class="agent-card__name">{{ agent.name }}</div>
              <div class="agent-card__desc">{{ agent.description }}</div>
            </div>
            <div class="agent-card__arrow">›</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentsStore } from '@/stores/agents'
import { AGENT_GROUPS } from '@/utils/constants'

const router = useRouter()
const agentsStore = useAgentsStore()
const searchText = ref('')

const groupNames = AGENT_GROUPS

const filteredGroups = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  const groups: Record<string, typeof agentsStore.agents> = {
    core: agentsStore.coreAgents,
    health: agentsStore.healthAgents,
    data: agentsStore.dataAgents,
  }
  if (!keyword) return groups
  const result: Record<string, typeof agentsStore.agents> = {}
  for (const [key, agents] of Object.entries(groups)) {
    const filtered = agents.filter(
      (a) =>
        a.name.toLowerCase().includes(keyword) ||
        a.description.toLowerCase().includes(keyword)
    )
    if (filtered.length > 0) {
      result[key] = filtered
    }
  }
  return result
})

function goToAgent(agentId: string) {
  agentsStore.activateAgent(agentId)
  router.push(`/chat/${agentId}`)
}
</script>

<style lang="less" scoped>
.agents-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-bg);

  &__search {
    background: var(--card-bg);
  }

  &__content {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    -webkit-overflow-scrolling: touch;
  }
}

.agent-group {
  margin-bottom: 20px;

  &__title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 10px;
    padding-left: 4px;
  }

  &__grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}

.agent-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--card-bg);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:active {
    background: var(--primary-light);
  }

  &__icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: var(--app-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
  }

  &__info {
    flex: 1;
    min-width: 0;
  }

  &__name {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
  }

  &__desc {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 2px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  &__arrow {
    font-size: 20px;
    color: var(--text-hint);
    flex-shrink: 0;
  }
}
</style>
