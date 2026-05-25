<template>
  <div class="health-page">
    <PageHeader title="健康中心" />
    <div class="health-page__content">
      <!-- Period Toggle -->
      <div class="period-toggle">
        <div class="period-toggle__item" :class="{ 'period-toggle__item--active': period === 'today' }" @click="period = 'today'">今日</div>
        <div class="period-toggle__item" :class="{ 'period-toggle__item--active': period === 'weekly' }" @click="period = 'weekly'">本周</div>
      </div>

      <!-- Loading skeleton -->
      <div v-if="loadingMetrics" class="loading-skeleton">
        <div class="skeleton-grid">
          <div v-for="n in 6" :key="n" class="skeleton-card"></div>
        </div>
      </div>

      <!-- Metrics Error -->
      <ErrorRetry v-else-if="metricsError" text="健康数据加载失败" @retry="loadMetrics" />

      <!-- Metrics Grid -->
      <template v-else>
        <div class="metrics-grid">
          <div v-for="metric in metrics" :key="metric.key" class="metric-card" @click="openMetricEditor(metric.key)">
            <div class="metric-card__icon">{{ metric.icon }}</div>
            <div class="metric-card__value">{{ metric.value }}</div>
            <div class="metric-card__label">{{ metric.label }}</div>
            <div v-if="metric.sub" class="metric-card__sub">{{ metric.sub }}</div>
          </div>
        </div>
      </template>

      <!-- Diet Section -->
      <div class="section-card">
        <div class="section-card__header">
          <span class="section-card__title">饮食摄入</span>
          <span class="section-card__action" @click="$router.push('/nutrition')">查看详情 ›</span>
        </div>
        <div v-if="loadingDiet" class="diet-skeleton">
          <LoadingSkeleton height="32px" :lines="3" />
        </div>
        <ErrorRetry v-else-if="dietError" text="饮食数据加载失败" @retry="loadDiet" />
        <div v-else class="diet-summary">
          <div class="diet-summary__calories">
            <div class="diet-summary__number">{{ dietCalories }}</div>
            <div class="diet-summary__unit">/ {{ dietGoal.toLocaleString() }} kcal</div>
          </div>
          <div class="diet-summary__bars">
            <div class="diet-bar">
              <span class="diet-bar__label">蛋白质</span>
              <div class="diet-bar__track"><div class="diet-bar__fill diet-bar__fill--protein" :style="{ width: proteinPct + '%' }"></div></div>
              <span class="diet-bar__value">{{ dietProtein }}g</span>
            </div>
            <div class="diet-bar">
              <span class="diet-bar__label">碳水</span>
              <div class="diet-bar__track"><div class="diet-bar__fill diet-bar__fill--carbs" :style="{ width: carbsPct + '%' }"></div></div>
              <span class="diet-bar__value">{{ dietCarbs }}g</span>
            </div>
            <div class="diet-bar">
              <span class="diet-bar__label">脂肪</span>
              <div class="diet-bar__track"><div class="diet-bar__fill diet-bar__fill--fat" :style="{ width: fatPct + '%' }"></div></div>
              <span class="diet-bar__value">{{ dietFat }}g</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Metric Editor Popup -->
      <div v-if="editingMetric" class="editor-overlay" @click.self="closeEditor">
        <div class="editor-panel">
          <div class="editor-panel__title">录入{{ editingLabel }}</div>
          <input
            v-model.number="editValue"
            type="number"
            class="editor-panel__input"
            :placeholder="editPlaceholder"
            autofocus
          />
          <div class="editor-panel__actions">
            <button class="editor-panel__cancel" @click="closeEditor">取消</button>
            <button class="editor-panel__save" @click="saveMetric">保存</button>
          </div>
        </div>
      </div>

      <!-- Connect Device Guide -->
      <div class="section-card">
        <div class="section-card__header">
          <span class="section-card__title">连接设备</span>
        </div>
        <div class="device-list">
          <div class="device-card device-card--inactive">
            <div class="device-card__icon">⌚</div>
            <div class="device-card__info">
              <div class="device-card__name">Apple Watch</div>
              <div class="device-card__desc">自动同步步数、心率、运动数据</div>
            </div>
            <div class="device-card__badge">即将支持</div>
          </div>
          <div class="device-card device-card--inactive">
            <div class="device-card__icon">📱</div>
            <div class="device-card__info">
              <div class="device-card__name">华为运动健康</div>
              <div class="device-card__desc">同步运动记录、睡眠数据</div>
            </div>
            <div class="device-card__badge">即将支持</div>
          </div>
          <div class="device-card" @click="$router.push('/nutrition')">
            <div class="device-card__icon">📸</div>
            <div class="device-card__info">
              <div class="device-card__name">AI 饮食记录</div>
              <div class="device-card__desc">拍照识别食物，自动计算热量</div>
            </div>
            <div class="device-card__arrow">›</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import PageHeader from '@/components/layout/PageHeader.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import ErrorRetry from '@/components/common/ErrorRetry.vue'
import apiClient from '@/api/client'
import { getTodayHealthMetrics, getTodayDietSummary } from '@/api/health'
import { useHealthStore } from '@/stores/health'
import type { HealthMetrics, DietSummary } from '@/api/health'

const healthStore = useHealthStore()
const period = ref<'today' | 'weekly'>('today')
const dietData = ref<DietSummary | null>(null)
const loadingMetrics = ref(true)
const loadingDiet = ref(false)
const metricsError = ref(false)
const dietError = ref(false)

const editingMetric = ref('')
const editValue = ref<number>(0)

const METRIC_LABELS: Record<string, string> = {
  steps: '步数', sleep: '睡眠分钟', exercise: '运动分钟', weight: '体重(kg)',
  hr: '心率', calories: '消耗热量',
}
const METRIC_PLACEHOLDERS: Record<string, string> = {
  steps: '输入今日步数', sleep: '输入睡眠分钟数', exercise: '输入运动分钟数',
  weight: '输入体重(kg)', hr: '输入平均心率', calories: '输入消耗热量',
}
const METRIC_API_KEYS: Record<string, string> = {
  steps: 'steps', sleep: 'sleep_minutes', exercise: 'exercise_minutes',
  weight: 'weight_kg', hr: 'heart_rate_avg', calories: 'calories_burned',
}

const editingLabel = computed(() => METRIC_LABELS[editingMetric.value] || '')
const editPlaceholder = computed(() => METRIC_PLACEHOLDERS[editingMetric.value] || '')

const MACRO_GOALS = { protein: 90, carbs: 260, fat: 73 }

const metrics = computed(() => {
  const m = healthStore.todayMetrics
  if (period.value === 'today') {
    return [
      { key: 'steps', icon: '👟', value: m ? m.steps.toLocaleString() : '6,842', label: '步数', sub: '目标 10,000' },
      { key: 'hr', icon: '❤️', value: m ? String(m.heartRate) : '72', label: '心率 bpm', sub: '静息' },
      { key: 'sleep', icon: '😴', value: m ? (m.sleepMinutes / 60).toFixed(1) + 'h' : '7.5h', label: '睡眠', sub: '质量良好' },
      { key: 'calories', icon: '🔥', value: m ? String(m.caloriesBurned) : '328', label: '消耗 kcal', sub: '运动消耗' },
      { key: 'exercise', icon: '🏃', value: m ? m.exerciseMinutes + 'min' : '35min', label: '运动时长', sub: '' },
      { key: 'weight', icon: '⚖️', value: m && m.weight ? String(m.weight) : '68.5', label: '体重 kg', sub: '-0.2' },
    ]
  }
  return [
    { key: 'steps', icon: '👟', value: '42,156', label: '总步数', sub: '日均 6,022' },
    { key: 'hr', icon: '❤️', value: '68', label: '平均心率', sub: '最低 52' },
    { key: 'sleep', icon: '😴', value: '7.2h', label: '平均睡眠', sub: '5 天达标' },
    { key: 'calories', icon: '🔥', value: '2,180', label: '总消耗', sub: '日均 311' },
    { key: 'exercise', icon: '🏃', value: '4次', label: '运动次数', sub: '共 3h20m' },
    { key: 'weight', icon: '⚖️', value: '-0.5', label: '体重变化 kg', sub: '趋势良好' },
  ]
})

const dietCalories = computed(() => dietData.value ? Math.round(dietData.value.totalCalories) : 0)
const dietGoal = computed(() => dietData.value?.goalCalories || 2200)
const dietProtein = computed(() => dietData.value ? Math.round(dietData.value.protein) : 0)
const dietCarbs = computed(() => dietData.value ? Math.round(dietData.value.carbs) : 0)
const dietFat = computed(() => dietData.value ? Math.round(dietData.value.fat) : 0)
const proteinPct = computed(() => Math.min(100, Math.round((dietProtein.value / MACRO_GOALS.protein) * 100)))
const carbsPct = computed(() => Math.min(100, Math.round((dietCarbs.value / MACRO_GOALS.carbs) * 100)))
const fatPct = computed(() => Math.min(100, Math.round((dietFat.value / MACRO_GOALS.fat) * 100)))

onMounted(async () => { await Promise.all([loadMetrics(), loadDiet()]) })

async function loadMetrics() {
  loadingMetrics.value = true
  metricsError.value = false
  try {
    const data = await getTodayHealthMetrics() as unknown as HealthMetrics
    if (data) healthStore.setMetrics('today', data)
  } catch { metricsError.value = true }
  finally { loadingMetrics.value = false }
}

async function loadDiet() {
  loadingDiet.value = true
  dietError.value = false
  try {
    const data = await getTodayDietSummary() as unknown as DietSummary
    if (data) { dietData.value = data; healthStore.setDietSummary(data) }
  } catch { dietError.value = true }
  finally { loadingDiet.value = false }
}

function openMetricEditor(key: string) {
  if (period.value !== 'today') return
  editingMetric.value = key
  editValue.value = 0
}

function closeEditor() { editingMetric.value = '' }

async function saveMetric() {
  const apiKey = METRIC_API_KEYS[editingMetric.value]
  if (!apiKey) return

  try {
    await apiClient.post('/health/metrics', { [apiKey]: editValue.value })
    await loadMetrics()
  } catch { /* silent */ }
  closeEditor()
}
</script>

<style lang="less" scoped>
.health-page {
  display: flex; flex-direction: column; height: 100%; background: var(--app-bg);
  &__content { flex: 1; overflow-y: auto; padding: 12px; -webkit-overflow-scrolling: touch; }
}

.period-toggle {
  display: flex; background: var(--card-bg); border-radius: 8px; padding: 3px; margin-bottom: 16px;
  &__item {
    flex: 1; text-align: center; padding: 8px; font-size: 14px;
    color: var(--text-secondary); border-radius: 6px; cursor: pointer; transition: all 0.2s;
    &--active { background: var(--primary-color); color: #fff; font-weight: 600; }
  }
}

.loading-skeleton { margin-bottom: 16px; }
.skeleton-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.skeleton-card {
  background: var(--card-bg); border-radius: 12px; height: 90px;
  animation: shimmer 1.5s infinite;
  background: linear-gradient(90deg, var(--card-bg) 25%, var(--border-color) 50%, var(--card-bg) 75%);
  background-size: 200% 100%;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

.loading-text { text-align: center; padding: 24px; font-size: 13px; color: var(--text-secondary); }

.metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px; }

.metric-card {
  background: var(--card-bg); border-radius: 12px; padding: 14px; cursor: pointer; transition: transform 0.2s;
  &:active { transform: scale(0.97); }
  &__icon { font-size: 22px; margin-bottom: 6px; }
  &__value { font-size: 22px; font-weight: 700; color: var(--text-primary); }
  &__label { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
  &__sub { font-size: 11px; color: var(--text-hint); margin-top: 2px; }
}

/* Editor */
.editor-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); z-index: 200; display: flex; align-items: center; justify-content: center;
}
.editor-panel {
  background: var(--card-bg); border-radius: 16px; padding: 24px; width: 280px;
  &__title { font-size: 16px; font-weight: 600; margin-bottom: 16px; text-align: center; }
  &__input {
    width: 100%; padding: 10px 14px; border: 1px solid var(--border-color); border-radius: 8px;
    font-size: 18px; text-align: center; outline: none;
    &:focus { border-color: var(--primary-color); }
  }
  &__actions { display: flex; gap: 10px; margin-top: 16px; }
  &__cancel {
    flex: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px;
    background: transparent; font-size: 14px; cursor: pointer; color: var(--text-secondary);
  }
  &__save {
    flex: 1; padding: 10px; border: none; border-radius: 8px;
    background: var(--primary-color); color: #fff; font-size: 14px; font-weight: 600; cursor: pointer;
  }
}

.section-card {
  background: var(--card-bg); border-radius: 12px; padding: 14px; margin-bottom: 12px;
  &__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
  &__title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
  &__action { font-size: 13px; color: var(--primary-color); cursor: pointer; }
}

.diet-summary {
  &__calories { display: flex; align-items: baseline; gap: 4px; margin-bottom: 14px; }
  &__number { font-size: 28px; font-weight: 700; color: var(--text-primary); }
  &__unit { font-size: 14px; color: var(--text-secondary); }
}

.diet-bar {
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
  &__label { font-size: 12px; color: var(--text-secondary); width: 42px; flex-shrink: 0; }
  &__track { flex: 1; height: 6px; background: var(--app-bg); border-radius: 3px; overflow: hidden; }
  &__fill { height: 100%; border-radius: 3px; transition: width 0.5s ease;
    &--protein { background: #ff6b6b; }
    &--carbs { background: #ffc107; }
    &--fat { background: #4ecdc4; }
  }
  &__value { font-size: 12px; color: var(--text-primary); font-weight: 600; width: 36px; text-align: right; flex-shrink: 0; }
}

/* Device guide */
.device-card {
  display: flex; align-items: center; gap: 10px; padding: 12px;
  background: var(--app-bg); border-radius: 10px; margin-bottom: 8px; cursor: pointer;
  transition: transform 0.2s;
  &:active { transform: scale(0.98); }
  &:last-child { margin-bottom: 0; }
  &--inactive { opacity: 0.6; cursor: default; &:active { transform: none; } }
  &__icon { font-size: 28px; width: 44px; text-align: center; flex-shrink: 0; }
  &__info { flex: 1; }
  &__name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
  &__desc { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
  &__badge { font-size: 11px; color: var(--text-hint); padding: 3px 8px; background: var(--border-color); border-radius: 10px; flex-shrink: 0; }
  &__arrow { font-size: 20px; color: var(--text-hint); flex-shrink: 0; }
}
</style>
