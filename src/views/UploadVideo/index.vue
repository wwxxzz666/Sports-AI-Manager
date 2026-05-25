<template>
  <div class="upload-video-page">
    <PageHeader title="动作分析" :show-back="true" />
    <div class="upload-video-page__content">
      <!-- Step 1: Upload (hidden when analyzing or showing result) -->
      <template v-if="!analyzing && !analysisResult">
        <div class="capture-zone" @click="triggerUpload">
          <div v-if="!selectedVideo" class="capture-zone__placeholder">
            <div class="capture-zone__icon">📹</div>
            <div class="capture-zone__text">点击拍摄或上传运动视频</div>
            <div class="capture-zone__hint">支持 MP4/MOV/WebM，最大 {{ maxSize }}MB</div>
          </div>
          <div v-else class="capture-zone__preview">
            <span class="capture-zone__check">✅</span>
            <span class="capture-zone__file-name">{{ selectedVideo.name }}</span>
            <div class="capture-zone__remove" @click.stop="selectedVideo = null">✕</div>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            accept="video/*"
            style="display: none"
            @change="handleFileSelect"
          />
        </div>

        <div class="sport-selector">
          <div class="sport-selector__title">选择运动项目</div>
          <div class="sport-selector__chips">
            <div
              v-for="sport in sports"
              :key="sport"
              class="sport-chip"
              :class="{ 'sport-chip--active': selectedSport === sport }"
              @click="selectedSport = sport"
            >
              {{ sport }}
            </div>
          </div>
        </div>

        <div class="goal-input">
          <div class="goal-input__title">分析目标（可选）</div>
          <textarea
            v-model="analysisGoal"
            class="goal-input__textarea"
            placeholder="想改善什么？例如：深蹲时膝盖总是内扣"
            rows="3"
          />
        </div>

        <div class="action-bar">
          <button
            class="action-bar__btn"
            :disabled="!canAnalyze"
            @click="startAnalysis"
          >
            开始分析
          </button>
        </div>
      </template>

      <!-- Step 2: Analyzing -->
      <div v-if="analyzing" class="analyzing-section">
        <div class="analyzing-section__spinner"></div>
        <div class="analyzing-section__text">AI 正在分析 {{ selectedSport }} 动作...</div>
        <div class="analyzing-section__hint">这可能需要几秒钟</div>
      </div>

      <!-- Step 3: Result -->
      <ErrorRetry v-if="analysisError && !analyzing" text="动作分析失败" @retry="startAnalysis" />
      <div v-else-if="analysisResult && !analyzing" class="result-section">
        <!-- Score Card -->
        <div class="score-card">
          <div class="score-card__value">{{ analysisResult.overall_score }}</div>
          <div class="score-card__label">综合评分</div>
          <div class="score-card__bar-track">
            <div
              class="score-card__bar-fill"
              :style="{ width: analysisResult.overall_score + '%' }"
            ></div>
          </div>
          <div class="score-card__sport">{{ analysisResult.sport_type }}</div>
        </div>

        <!-- Posture Issues -->
        <div v-if="analysisResult.posture_issues.length > 0" class="section-card">
          <div class="section-card__title">姿态分析</div>
          <div class="issue-list">
            <div
              v-for="(issue, i) in analysisResult.posture_issues"
              :key="i"
              class="issue-item issue-item--warn"
            >
              <span class="issue-item__dot"></span>
              {{ issue }}
            </div>
          </div>
        </div>

        <!-- Suggestions -->
        <div v-if="analysisResult.suggestions.length > 0" class="section-card">
          <div class="section-card__title">改进建议</div>
          <div class="issue-list">
            <div
              v-for="(s, i) in analysisResult.suggestions"
              :key="i"
              class="issue-item issue-item--suggest"
            >
              <span class="issue-item__num">{{ i + 1 }}</span>
              {{ s }}
            </div>
          </div>
        </div>

        <!-- Risks -->
        <div v-if="analysisResult.risks.length > 0" class="section-card section-card--risk">
          <div class="section-card__title">风险提示</div>
          <div class="issue-list">
            <div
              v-for="(risk, i) in analysisResult.risks"
              :key="i"
              class="issue-item issue-item--danger"
            >
              <span class="issue-item__icon">⚠️</span>
              {{ risk }}
            </div>
          </div>
        </div>

        <!-- Recommended Training -->
        <div v-if="analysisResult.recommended_training.length > 0" class="section-card">
          <div class="section-card__title">推荐训练</div>
          <div class="training-list">
            <div
              v-for="(t, i) in analysisResult.recommended_training"
              :key="i"
              class="training-item"
            >
              <span class="training-item__icon">🏋️</span>
              {{ t }}
            </div>
          </div>
        </div>

        <!-- Disclaimer -->
        <div class="disclaimer">{{ analysisResult.disclaimer }}</div>

        <!-- Actions -->
        <div class="result-actions">
          <button class="result-actions__reset" @click="resetAnalysis">重新分析</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import PageHeader from '@/components/layout/PageHeader.vue'
import ErrorRetry from '@/components/common/ErrorRetry.vue'
import { analyzeMotion, type MotionAnalysisResult } from '@/api/motion'

const fileInputRef = ref<HTMLInputElement>()
const selectedVideo = ref<File | null>(null)
const selectedSport = ref('')
const analysisGoal = ref('')
const analyzing = ref(false)
const analysisError = ref(false)
const analysisResult = ref<MotionAnalysisResult | null>(null)
const maxSize = 100

const sports = ['跑步', '深蹲', '硬拉', '卧推', '瑜伽', '游泳', '篮球', '网球', '羽毛球', '其他']

const canAnalyze = computed(() => selectedVideo.value && selectedSport.value && !analyzing.value)

function triggerUpload() {
  fileInputRef.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files?.[0]) {
    selectedVideo.value = target.files[0]
  }
}

async function startAnalysis() {
  if (!canAnalyze.value || !selectedVideo.value) return
  analyzing.value = true
  analysisError.value = false
  analysisResult.value = null

  try {
    const result = await analyzeMotion(
      selectedVideo.value,
      selectedSport.value,
      analysisGoal.value || undefined
    )
    analysisResult.value = result
  } catch {
    analysisError.value = true
  } finally {
    analyzing.value = false
  }
}

function resetAnalysis() {
  analysisResult.value = null
  analysisError.value = false
  selectedVideo.value = null
}
</script>

<style lang="less" scoped>
.upload-video-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-bg);

  &__content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    padding-bottom: 32px;
    -webkit-overflow-scrolling: touch;
  }
}

.capture-zone {
  background: var(--card-bg);
  border-radius: 12px;
  border: 2px dashed var(--border-color);
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s;
  margin-bottom: 20px;

  &:active { border-color: var(--primary-color); }
  &__placeholder { text-align: center; }
  &__icon { font-size: 40px; margin-bottom: 12px; }
  &__text { font-size: 15px; color: var(--text-primary); font-weight: 500; }
  &__hint { font-size: 12px; color: var(--text-hint); margin-top: 6px; }
  &__preview { display: flex; align-items: center; gap: 12px; padding: 16px; }
  &__check { font-size: 20px; }
  &__file-name { font-size: 14px; color: var(--text-primary); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  &__remove {
    width: 28px; height: 28px; border-radius: 50%;
    background: var(--app-bg); display: flex; align-items: center; justify-content: center;
    font-size: 14px; color: var(--text-secondary); cursor: pointer; flex-shrink: 0;
  }
}

.sport-selector { margin-bottom: 20px;
  &__title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 10px; }
  &__chips { display: flex; flex-wrap: wrap; gap: 8px; }
}

.sport-chip {
  padding: 8px 16px; border-radius: 20px;
  background: var(--card-bg); font-size: 13px;
  color: var(--text-primary); cursor: pointer;
  transition: all 0.2s; border: 1px solid var(--border-color);
  &--active { background: var(--primary-color); color: #fff; border-color: var(--primary-color); }
}

.goal-input { margin-bottom: 24px;
  &__title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 10px; }
  &__textarea {
    width: 100%; padding: 12px; border: 1px solid var(--border-color);
    border-radius: 8px; background: var(--card-bg); font-size: 14px;
    color: var(--text-primary); resize: none; outline: none; font-family: inherit;
    &:focus { border-color: var(--primary-color); }
  }
}

.action-bar {
  &__btn {
    width: 100%; height: 48px; border: none; border-radius: 24px;
    background: var(--primary-color); color: #fff;
    font-size: 16px; font-weight: 600; cursor: pointer; transition: opacity 0.2s;
    &:disabled { background: var(--border-color); color: var(--text-hint); cursor: not-allowed; }
    &:not(:disabled):active { opacity: 0.85; }
  }
}

/* Analyzing */
.analyzing-section {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80px 0;
  &__spinner {
    width: 48px; height: 48px; border: 4px solid var(--border-color);
    border-top-color: var(--primary-color); border-radius: 50%;
    animation: spin 0.8s linear infinite; margin-bottom: 20px;
  }
  &__text { font-size: 16px; font-weight: 600; color: var(--text-primary); }
  &__hint { font-size: 13px; color: var(--text-secondary); margin-top: 8px; }
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Result */
.score-card {
  text-align: center; padding: 24px; background: var(--card-bg); border-radius: 16px; margin-bottom: 16px;
  &__value { font-size: 64px; font-weight: 800; color: var(--primary-color); line-height: 1; }
  &__label { font-size: 14px; color: var(--text-secondary); margin-top: 4px; }
  &__bar-track { height: 6px; background: var(--app-bg); border-radius: 3px; margin: 16px auto 0; max-width: 240px; overflow: hidden; }
  &__bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--primary-color), #07c160); transition: width 1s ease; }
  &__sport { font-size: 13px; color: var(--text-hint); margin-top: 8px; }
}

.section-card {
  background: var(--card-bg); border-radius: 12px; padding: 16px; margin-bottom: 12px;
  &--risk { border-left: 3px solid var(--danger-color); }
  &__title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; }
}

.issue-list { display: flex; flex-direction: column; gap: 8px; }

.issue-item {
  display: flex; align-items: flex-start; gap: 8px;
  font-size: 14px; color: var(--text-primary); line-height: 1.5;
  &__dot { width: 6px; height: 6px; border-radius: 50%; margin-top: 7px; flex-shrink: 0; }
  &__num { width: 20px; height: 20px; border-radius: 50%; background: var(--primary-color); color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  &__icon { font-size: 16px; flex-shrink: 0; }
  &--warn .issue-item__dot { background: var(--warning-color, #ffc107); }
  &--suggest .issue-item__dot { background: var(--primary-color); }
  &--danger { color: var(--danger-color); }
}

.training-item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 0; border-bottom: 1px solid var(--border-color);
  font-size: 14px; color: var(--text-primary);
  &:last-child { border-bottom: none; }
  &__icon { font-size: 20px; }
}

.disclaimer {
  text-align: center; font-size: 12px; color: var(--text-hint);
  padding: 16px; font-style: italic;
}

.result-actions { margin-top: 16px;
  &__reset {
    width: 100%; height: 44px; border: 1px solid var(--primary-color);
    border-radius: 22px; background: transparent; color: var(--primary-color);
    font-size: 15px; font-weight: 500; cursor: pointer; transition: opacity 0.2s;
    &:active { opacity: 0.7; }
  }
}
</style>
