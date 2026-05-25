<template>
  <div class="home-page">
    <!-- Greeting Header -->
    <div class="home-header">
      <div class="home-header__top">
        <div class="home-header__greeting">
          <span class="home-header__text">{{ greeting }}，{{ userStore.nickname }}</span>
          <span class="home-header__wave">👋</span>
        </div>
        <div class="home-header__mascot">🏃</div>
      </div>
      <div class="home-header__date">{{ todayDate }}</div>
    </div>

    <!-- Health Overview Strip (A02, A03) -->
    <div class="health-overview" :class="{ 'health-overview--expanded': healthExpanded }">
      <div class="health-overview__header" @click="healthExpanded = !healthExpanded">
        <span class="health-overview__title">健康概览</span>
        <span class="health-overview__toggle">{{ healthExpanded ? '收起' : '展开' }}</span>
      </div>
      <div v-show="healthExpanded" class="health-overview__scroll">
        <!-- Health data loading -->
        <div v-if="loadingHealth" class="health-overview__skeleton">
          <LoadingSkeleton width="72px" height="48px" :lines="1" />
          <LoadingSkeleton width="72px" height="48px" :lines="1" />
          <LoadingSkeleton width="72px" height="48px" :lines="1" />
          <LoadingSkeleton width="72px" height="48px" :lines="1" />
        </div>
        <!-- Health data error -->
        <ErrorRetry v-else-if="healthError" text="健康数据加载失败" @retry="refreshHealthData" />
        <!-- Health data -->
        <div v-else class="health-overview__cards">
          <div class="health-card" @click="goToHealth">
            <div class="health-card__icon">👟</div>
            <div class="health-card__value">{{ healthData.steps }}</div>
            <div class="health-card__label">今日步数</div>
          </div>
          <div class="health-card" @click="goToHealth">
            <div class="health-card__icon">🔥</div>
            <div class="health-card__value">{{ healthData.calories }}</div>
            <div class="health-card__label">消耗 kcal</div>
          </div>
          <div class="health-card" @click="goToHealth">
            <div class="health-card__icon">😴</div>
            <div class="health-card__value">{{ healthData.sleep }}</div>
            <div class="health-card__label">睡眠 h</div>
          </div>
          <div class="health-card" @click="goToNutrition">
            <div class="health-card__icon">🍎</div>
            <div class="health-card__value">{{ healthData.intake }}</div>
            <div class="health-card__label">今日摄入</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Agents Row (A04) -->
    <div class="quick-agents">
      <div class="quick-agents__title">快捷智能体</div>
      <div class="quick-agents__scroll">
        <div
          v-for="agent in quickAgentList"
          :key="agent.id"
          class="quick-agent-chip"
          @click="goToAgent(agent.id)"
        >
          <span class="quick-agent-chip__icon">{{ agent.icon }}</span>
          <span class="quick-agent-chip__name">{{ agent.name }}</span>
        </div>
      </div>
    </div>

    <!-- Recommended Questions -->
    <QuickReplies
      :questions="recommendedQuestions"
      @select="handleQuickQuestion"
    />

    <!-- Chat Stream (A05) -->
    <ChatStream
      :messages="conversationStore.messages"
      @retry="handleRetry"
    />

    <!-- Attachment Panel (A07) -->
    <AttachmentPanel
      v-model:show="showAttachPanel"
      @select="handleAttachSelect"
    />

    <!-- Input Bar (A05, A06) -->
    <ChatInputBar
      ref="inputBarRef"
      :disabled="conversationStore.isStreaming"
      :placeholder="conversationStore.isStreaming ? 'AI 正在思考中...' : '输入你的问题...'"
      @send="handleSend"
      @toggle-attach="showAttachPanel = true"
      @voice-input="handleVoiceInput"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAgentsStore } from '@/stores/agents'
import { useConversationStore } from '@/stores/conversation'
import { formatGreeting, formatDate, formatNumber } from '@/utils/format'
import { getTodayDietSummary, getTodayHealthMetrics, type DietSummary, type HealthMetrics } from '@/api/health'
import { sendChatMessage } from '@/api/chat'
import ChatStream from '@/components/chat/ChatStream.vue'
import ChatInputBar from '@/components/chat/ChatInputBar.vue'
import QuickReplies from '@/components/chat/QuickReplies.vue'
import AttachmentPanel from '@/components/chat/AttachmentPanel.vue'
import type { Message } from '@/stores/conversation'

const router = useRouter()
const userStore = useUserStore()
const agentsStore = useAgentsStore()
const conversationStore = useConversationStore()

const greeting = formatGreeting()
const todayDate = formatDate()
const healthExpanded = ref(true)
const showAttachPanel = ref(false)
const inputBarRef = ref<InstanceType<typeof ChatInputBar>>()
const loadingHealth = ref(true)
const healthError = ref(false)

const healthData = ref({ steps: '--', calories: '--', sleep: '--', intake: '--' })

// Agent routing: maps keywords to agent types
const AGENT_ROUTES: { keywords: string[]; agent: string }[] = [
  { keywords: ['吃', '饮食', '热量', '卡路里', 'kcal', '营养', '食物', '早餐', '午餐', '晚餐', '加餐', '零食', '摄入', '超标', '减肥', '增肌', '蛋白质', '碳水', '脂肪'], agent: 'food-calories' },
  { keywords: ['跑步', '运动', '锻炼', '训练', '健身', '深蹲', '瑜伽', '游泳', '打球', '打卡'], agent: 'workout-checkin' },
  { keywords: ['比赛', '活动', '找局', '篮球', '足球', '羽毛球', '约球'], agent: 'find-game' },
  { keywords: ['教练', '私教'], agent: 'find-coach' },
  { keywords: ['天气', '出门', '户外', '装备'], agent: 'go-out-prep' },
  { keywords: ['疼', '伤', '康复', '膝盖', '腰', '肩膀', '酸痛'], agent: 'rehab-coach' },
]

function routeAgent(text: string): string {
  const lower = text.toLowerCase()
  for (const route of AGENT_ROUTES) {
    if (route.keywords.some((kw) => lower.includes(kw))) return route.agent
  }
  return 'find-game'
}

const quickAgentList = computed(() => {
  if (agentsStore.recentAgents.length > 0) return agentsStore.recentAgents
  return agentsStore.agents.slice(0, 5)
})

const recommendedQuestions = [
  '今天适合户外运动吗？',
  '今天吃超了吗？',
  '运动后吃什么好？',
]

onMounted(async () => {
  const defaultAgent = agentsStore.agents[0]
  conversationStore.getOrCreateSession(defaultAgent.id)
  await Promise.all([loadHealthMetrics(), loadTodayIntake()])
})

async function loadHealthMetrics() {
  try {
    const data = await getTodayHealthMetrics() as unknown as HealthMetrics
    if (data) {
      healthData.value.steps = formatNumber(data.steps)
      healthData.value.calories = formatNumber(data.caloriesBurned)
      healthData.value.sleep = (data.sleepMinutes / 60).toFixed(1)
    }
  } catch { healthError.value = true }
}

async function loadTodayIntake() {
  try {
    const data = await getTodayDietSummary() as unknown as DietSummary
    if (data) {
      healthData.value.intake = formatNumber(Math.round(data.totalCalories || 0))
    }
  } catch { healthError.value = true }
}

async function refreshHealthData() {
  healthError.value = false
  loadingHealth.value = true
  await Promise.all([loadHealthMetrics(), loadTodayIntake()])
  loadingHealth.value = false
}

onMounted(async () => {
  const defaultAgent = agentsStore.agents[0]
  conversationStore.getOrCreateSession(defaultAgent.id)
  await refreshHealthData()
})

function goToHealth() { router.push('/health') }
function goToNutrition() { router.push('/nutrition') }
function goToAgent(agentId: string) {
  agentsStore.activateAgent(agentId)
  router.push(`/chat/${agentId}`)
}
function handleQuickQuestion(question: string) { handleSend(question) }

async function handleSend(text: string) {
  if (conversationStore.isStreaming) return

  conversationStore.addUserMessage(text)
  const assistantMsg = conversationStore.addAssistantPlaceholder()

  const targetAgent = routeAgent(text)
  try {
    const res = await sendChatMessage(targetAgent, { message: text })
    conversationStore.completeStreamingMessage(assistantMsg.id, res.reply)
    await Promise.all([loadHealthMetrics(), loadTodayIntake()])
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
  if (type === 'camera') {
    inputBarRef.value?.focus()
  } else if (type === 'video') {
    router.push('/upload-video')
  }
}

function handleVoiceInput() { /* placeholder */ }
</script>

<style lang="less" scoped>
.home-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-bg);
}

.home-header {
  padding: 16px;
  background: linear-gradient(135deg, #1989fa 0%, #07c160 100%);
  color: #fff;

  &__top { display: flex; align-items: center; justify-content: space-between; }
  &__greeting { display: flex; align-items: center; gap: 4px; }
  &__text { font-size: 20px; font-weight: 700; }
  &__wave { font-size: 22px; }
  &__mascot { font-size: 36px; }
  &__date { margin-top: 4px; font-size: 12px; opacity: 0.85; }
}

.health-overview {
  margin: 12px;
  background: var(--card-bg);
  border-radius: 12px;
  overflow: hidden;

  &__header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; cursor: pointer;
  }
  &__title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
  &__toggle { font-size: 12px; color: var(--primary-color); }
  &__scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  &__skeleton { display: flex; gap: 12px; padding: 0 16px 12px; }
  &__cards { display: flex; gap: 12px; padding: 0 16px 12px; min-width: max-content; }
}

.health-card {
  display: flex; flex-direction: column; align-items: center;
  padding: 12px 16px; background: var(--app-bg); border-radius: 10px;
  min-width: 80px; cursor: pointer; transition: transform 0.2s;
  &:active { transform: scale(0.96); }
  &__icon { font-size: 22px; margin-bottom: 6px; }
  &__value { font-size: 18px; font-weight: 700; color: var(--text-primary); }
  &__label { font-size: 11px; color: var(--text-secondary); margin-top: 2px; white-space: nowrap; }
}

.quick-agents { padding: 0 16px 8px;
  &__title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 10px; }
  &__scroll { display: flex; gap: 10px; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 4px; }
}

.quick-agent-chip {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px; background: var(--card-bg); border-radius: 20px;
  white-space: nowrap; cursor: pointer; transition: all 0.2s; flex-shrink: 0;
  &:active { background: var(--primary-light); }
  &__icon { font-size: 18px; }
  &__name { font-size: 13px; color: var(--text-primary); font-weight: 500; }
}
</style>
