<template>
  <div class="rating-page">
    <PageHeader title="AI 运动评级" />
    <div class="rating-page__content">
      <!-- Loading state -->
      <template v-if="loading">
        <div class="rating-skeleton">
          <LoadingSkeleton height="120px" :lines="1" />
          <LoadingSkeleton height="200px" :lines="1" />
        </div>
      </template>

      <!-- Error state -->
      <ErrorRetry v-else-if="loadError" text="评级数据加载失败" @retry="loadData" />

      <template v-else>
      <!-- Score Gauge -->
      <div class="score-section">
        <div class="score-gauge">
          <div class="score-gauge__number">{{ currentRating?.composite_score ?? '--' }}</div>
          <div class="score-gauge__label">综合评分</div>
        </div>
        <div class="score-meta">
          <div v-if="currentRating" class="tier-badge" :class="'tier-badge--' + tierColor">
            <span class="tier-badge__icon">{{ tierIcon }}</span>
            <span class="tier-badge__text">{{ currentRating.tier }}</span>
          </div>
          <div v-if="currentRating" class="percentile">超越 {{ currentRating.percentile }}% 用户</div>
        </div>
        <div class="refresh-btn" @click="handleRefresh">
          {{ refreshing ? '生成中...' : '刷新评级' }}
        </div>
      </div>

      <!-- Five Dimensions -->
      <div class="section-card">
        <div class="section-card__title">五维能力</div>
        <div class="radar-chart">
          <div v-for="dim in dimensions" :key="dim.key" class="dimension-item">
            <div class="dimension-item__label">{{ dim.label }}</div>
            <div class="dimension-item__bar">
              <div
                class="dimension-item__fill"
                :style="{ width: dim.value + '%' }"
              ></div>
            </div>
            <div class="dimension-item__value">{{ dim.value }}</div>
          </div>
        </div>
      </div>

      <!-- History -->
      <div class="section-card">
        <div class="section-card__title">历史记录</div>
        <div v-if="historyRecords.length > 0" class="history-list">
          <div v-for="record in historyRecords" :key="record.id" class="history-item">
            <div class="history-item__date">{{ record.date }}</div>
            <div class="history-item__score">
              <span class="history-item__number">{{ record.score }}</span>
              <span class="history-item__unit">分</span>
            </div>
            <div class="history-item__tier">{{ record.tier }}</div>
            <div
              class="history-item__delta"
              :class="{ positive: record.delta > 0, negative: record.delta < 0 }"
            >
              <template v-if="record.delta !== 0">{{ record.delta > 0 ? '+' : '' }}{{ record.delta }}</template>
              <template v-else>—</template>
            </div>
          </div>
        </div>
        <div v-else class="history-list__empty">暂无评级记录，点击上方按钮生成首次评级</div>
      </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import PageHeader from '@/components/layout/PageHeader.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import ErrorRetry from '@/components/common/ErrorRetry.vue'
import { generateRating, getCurrentRating, getRatingHistory } from '@/api/rating'
import type { CurrentRating, RatingHistoryItem } from '@/api/rating'

const currentRating = ref<CurrentRating | null>(null)
const historyRecords = ref<RatingHistoryItem[]>([])
const loading = ref(true)
const loadError = ref(false)
const refreshing = ref(false)

const dimLabels: Record<string, string> = {
  strength: '力量',
  endurance: '耐力',
  flexibility: '柔韧',
  consistency: '均衡',
  nutrition: '恢复',
}

const dimensions = computed(() => {
  if (!currentRating.value?.dimensions) {
    return [
      { key: 'strength', label: '力量', value: 0 },
      { key: 'endurance', label: '耐力', value: 0 },
      { key: 'flexibility', label: '柔韧', value: 0 },
      { key: 'consistency', label: '均衡', value: 0 },
      { key: 'nutrition', label: '恢复', value: 0 },
    ]
  }
  return Object.entries(currentRating.value.dimensions).map(([key, value]) => ({
    key,
    label: dimLabels[key] || key,
    value,
  }))
})

const tierColor = computed(() => {
  const t = currentRating.value?.tier || ''
  if (t.startsWith('青铜')) return 'bronze'
  if (t.startsWith('白银')) return 'silver'
  if (t.startsWith('黄金')) return 'gold'
  if (t.startsWith('钻石')) return 'diamond'
  if (t.startsWith('王者')) return 'king'
  return 'gold'
})

const tierIcon = computed(() => {
  const m: Record<string, string> = {
    bronze: '🟤', silver: '⚪', gold: '⭐', diamond: '💎', king: '👑',
  }
  return m[tierColor.value] || '⭐'
})

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  loadError.value = false
  try {
    const [rating, history] = await Promise.all([
      getCurrentRating(),
      getRatingHistory(),
    ])
    if (rating) currentRating.value = rating
    if (history) historyRecords.value = history
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

async function handleRefresh() {
  refreshing.value = true
  try {
    const newRating = await generateRating()
    if (newRating) {
      currentRating.value = newRating
      const history = await getRatingHistory()
      if (history) historyRecords.value = history
    }
  } catch {
    loadError.value = true
  } finally {
    refreshing.value = false
  }
}
</script>

<style lang="less" scoped>
.rating-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-bg);

  &__content {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    -webkit-overflow-scrolling: touch;
  }
}

.rating-skeleton {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-section {
  text-align: center;
  padding: 24px 0 16px;
}

.score-gauge {
  &__number {
    font-size: 56px;
    font-weight: 800;
    color: var(--primary-color);
    line-height: 1;
  }
  &__label {
    font-size: 14px;
    color: var(--text-secondary);
    margin-top: 4px;
  }
}

.score-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.tier-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  border-radius: 20px;

  &--bronze { background: linear-gradient(135deg, #cd7f32, #a0522d); }
  &--silver { background: linear-gradient(135deg, #c0c0c0, #808080); }
  &--gold { background: linear-gradient(135deg, #ffd700, #ffaa00); }
  &--diamond { background: linear-gradient(135deg, #00bfff, #1e90ff); }
  &--king { background: linear-gradient(135deg, #ff4500, #ff0000); }

  &__icon { font-size: 16px; }
  &__text { font-size: 14px; font-weight: 600; color: #fff; }
}

.percentile { font-size: 14px; color: var(--text-secondary); }

.refresh-btn {
  display: inline-block;
  margin-top: 16px;
  padding: 8px 24px;
  border-radius: 20px;
  background: var(--card-bg);
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--border-color);

  &:active { background: var(--primary-light); }
}

.section-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;

  &__title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
  }
}

.dimension-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;

  &__label {
    width: 36px;
    font-size: 13px;
    color: var(--text-secondary);
    flex-shrink: 0;
  }

  &__bar {
    flex: 1;
    height: 8px;
    background: var(--app-bg);
    border-radius: 4px;
    overflow: hidden;
  }

  &__fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--primary-color), #07c160);
    transition: width 0.8s ease;
  }

  &__value {
    width: 28px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    text-align: right;
    flex-shrink: 0;
  }
}

.history-list {
  &__empty { text-align: center; padding: 24px; font-size: 13px; color: var(--text-hint); }
}

.history-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);

  &:last-child { border-bottom: none; }

  &__date { font-size: 13px; color: var(--text-secondary); width: 90px; flex-shrink: 0; }
  &__score { flex: 1; }
  &__number { font-size: 18px; font-weight: 700; color: var(--text-primary); }
  &__unit { font-size: 12px; color: var(--text-secondary); margin-left: 2px; }
  &__tier { font-size: 13px; font-weight: 500; margin-right: 12px; }
  &__delta {
    font-size: 13px; font-weight: 600; width: 36px; text-align: right;
    &.positive { color: var(--success-color); }
    &.negative { color: var(--danger-color); }
  }
}
</style>
