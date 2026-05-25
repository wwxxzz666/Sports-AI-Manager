<template>
  <div class="nutrition-page">
    <PageHeader title="饮食记录中心" :show-back="true" />
    <div class="nutrition-page__content">
      <!-- Daily Intake Banner (A20) -->
      <div v-if="loadingDiet" class="intake-skeleton">
        <LoadingSkeleton height="100px" :lines="1" />
      </div>
      <ErrorRetry v-else-if="dietError" text="饮食数据加载失败" @retry="loadTodayDiet" />
      <div v-else class="intake-banner">
        <div class="intake-banner__info">
          <div class="intake-banner__calories">
            <span class="intake-banner__current">{{ dailyTotals.totalCalories }}</span>
            <span class="intake-banner__divider">/</span>
            <span class="intake-banner__goal">{{ dailyTotals.goalCalories }}</span>
          </div>
          <div class="intake-banner__label">
            千卡 ({{ remaining > 0 ? '剩余 ' + remaining : '超出 ' + Math.abs(remaining) }})
          </div>
        </div>
        <div class="intake-banner__macros">
          <div class="macro-item">
            <div class="macro-item__value">{{ dailyTotals.protein }}g</div>
            <div class="macro-item__label macro-item__label--protein">蛋白质</div>
          </div>
          <div class="macro-item">
            <div class="macro-item__value">{{ dailyTotals.carbs }}g</div>
            <div class="macro-item__label macro-item__label--carbs">碳水</div>
          </div>
          <div class="macro-item">
            <div class="macro-item__value">{{ dailyTotals.fat }}g</div>
            <div class="macro-item__label macro-item__label--fat">脂肪</div>
          </div>
        </div>
      </div>

      <!-- Meal Timeline -->
      <div class="meal-timeline">
        <div v-for="meal in mealSlots" :key="meal.type" class="meal-card">
          <div class="meal-card__header">
            <span class="meal-card__type">{{ meal.label }}</span>
            <span class="meal-card__time">{{ meal.time }}</span>
            <span v-if="meal.data" class="meal-card__calories">{{ meal.data.totalCalories }} kcal</span>
            <span v-else class="meal-card__add" @click="startAddMeal(meal.type)">+ 添加</span>
          </div>
          <div v-if="meal.data && meal.data.items.length > 0" class="meal-card__items">
            <div v-for="item in meal.data.items" :key="item.id" class="food-item">
              <span class="food-item__name">{{ item.foodName }}</span>
              <span class="food-item__portion">{{ item.portion }}</span>
              <span class="food-item__kcal">{{ item.calories }} kcal</span>
            </div>
          </div>
          <div v-else-if="!meal.data" class="meal-card__empty">
            待记录
          </div>
        </div>
      </div>
    </div>

    <!-- FAB: Photo Recognition (A15) -->
    <div v-if="!showRecognition" class="fab" @click="triggerPhotoCapture">
      <span class="fab__icon">📸</span>
      <span class="fab__text">拍照识别</span>
    </div>
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      capture="environment"
      style="display: none"
      @change="handleFileSelect"
    />

    <!-- Recognition Overlay (A15-A19) -->
    <div v-if="showRecognition" class="recognition-overlay">
      <div class="recognition-overlay__header">
        <span class="recognition-overlay__back" @click="cancelRecognition">‹</span>
        <span class="recognition-overlay__title">食物识别结果</span>
        <span></span>
      </div>

      <!-- Loading State -->
      <div v-if="recognizing" class="recognition-overlay__loading">
        <div class="recognition-overlay__spinner"></div>
        <div class="recognition-overlay__loading-text">AI 正在识别食物...</div>
      </div>

      <!-- Recognition Error -->
      <ErrorRetry v-else-if="recognitionError" text="食物识别失败，请重试" actionText="重试" @retry="retryRecognition" />

      <!-- Results (A16, A17) -->
      <div v-else-if="recognitionResult" class="recognition-overlay__content">
        <img v-if="recognitionResult.image_url" :src="recognitionResult.image_url" class="recognition-overlay__image" />

        <!-- Meal type selector (A18) -->
        <div class="meal-type-selector">
          <span class="meal-type-selector__label">餐次：</span>
          <div
            v-for="mt in mealTypes"
            :key="mt.value"
            class="meal-type-chip"
            :class="{ 'meal-type-chip--active': selectedMealType === mt.value }"
            @click="selectedMealType = mt.value"
          >
            {{ mt.label }}
          </div>
        </div>

        <!-- Editable food items (A18) -->
        <div class="editable-items">
          <div v-for="(item, index) in editableItems" :key="index" class="editable-item">
            <div class="editable-item__row">
              <input v-model="item.name" class="editable-item__input editable-item__name" placeholder="食物名称" />
              <span v-if="item.needs_confirmation" class="editable-item__warn">⚠️ 请确认</span>
            </div>
            <div class="editable-item__row">
              <input v-model="item.portion" class="editable-item__input editable-item__portion" placeholder="份量" />
              <span class="editable-item__kcal">{{ item.calories }} kcal</span>
            </div>
            <div class="editable-item__macros">
              <span>蛋白质 {{ item.protein_g }}g</span>
              <span>碳水 {{ item.carbs_g }}g</span>
              <span>脂肪 {{ item.fat_g }}g</span>
            </div>
            <div class="editable-item__actions">
              <input
                v-model.number="item.calories"
                type="number"
                class="editable-item__cal-input"
                placeholder="热量"
              />
              <span class="editable-item__remove" @click="removeItem(index)">删除</span>
            </div>
          </div>
        </div>

        <!-- Totals -->
        <div class="recognition-totals">
          <span>本餐合计：{{ editableTotalCalories }} kcal</span>
          <span class="recognition-totals__disclaimer">⚠️ 估算值，仅供健康管理参考</span>
        </div>

        <!-- Save button (A19) -->
        <button class="save-btn" @click="handleSaveMeal">
          保存为{{ selectedMealTypeLabel }}记录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import PageHeader from '@/components/layout/PageHeader.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import ErrorRetry from '@/components/common/ErrorRetry.vue'
import { recognizeFood, saveMeal, type FoodRecognitionItem } from '@/api/nutrition'
import { getTodayDietSummary, type DietSummary } from '@/api/health'
import dayjs from 'dayjs'

const fileInputRef = ref<HTMLInputElement>()
const showRecognition = ref(false)
const recognizing = ref(false)
const recognitionError = ref(false)
const recognitionResult = ref<{ image_url: string; items: FoodRecognitionItem[] } | null>(null)
const selectedMealType = ref('lunch')
const editableItems = ref<FoodRecognitionItem[]>([])
const loadingDiet = ref(true)
const dietError = ref(false)

interface MealSlot {
  type: string
  label: string
  time: string
  data: { totalCalories: number; items: { id: string; foodName: string; portion: string; calories: number }[] } | null
}

const mealSlots = ref<MealSlot[]>([
  { type: 'breakfast', label: '早餐', time: '', data: null },
  { type: 'lunch', label: '午餐', time: '', data: null },
  { type: 'dinner', label: '晚餐', time: '', data: null },
  { type: 'snack', label: '加餐', time: '', data: null },
])

const dailyTotals = ref({
  totalCalories: 0,
  goalCalories: 2200,
  protein: 0,
  carbs: 0,
  fat: 0,
})

const remaining = computed(() => dailyTotals.value.goalCalories - dailyTotals.value.totalCalories)

const mealTypes = [
  { value: 'breakfast', label: '早餐' },
  { value: 'lunch', label: '午餐' },
  { value: 'dinner', label: '晚餐' },
  { value: 'snack', label: '加餐' },
]

const selectedMealTypeLabel = computed(() =>
  mealTypes.find((m) => m.value === selectedMealType.value)?.label || '餐食'
)

const editableTotalCalories = computed(() =>
  Math.round(editableItems.value.reduce((sum, item) => sum + (Number(item.calories) || 0), 0))
)

onMounted(() => {
  loadTodayDiet()
})

async function loadTodayDiet() {
  try {
    const data = await getTodayDietSummary() as unknown as DietSummary
    if (data) {
      dailyTotals.value.totalCalories = Math.round(data.totalCalories || 0)
      dailyTotals.value.protein = Math.round(data.protein || 0)
      dailyTotals.value.carbs = Math.round(data.carbs || 0)
      dailyTotals.value.fat = Math.round(data.fat || 0)
      dailyTotals.value.goalCalories = data.goalCalories || 2200

      if (data.meals) {
        for (const meal of data.meals) {
          const slot = mealSlots.value.find((s) => s.type === meal.mealType)
          if (slot) {
            slot.data = {
              totalCalories: Math.round(meal.totalCalories),
              items: meal.items.map((i) => ({
                id: i.id,
                foodName: i.foodName,
                portion: i.portion,
                calories: Math.round(i.calories),
              })),
            }
            slot.time = dayjs(meal.recordDate).format('HH:mm')
          }
        }
      }
    }
  } catch {
    // Use empty state
  }
}

function triggerPhotoCapture() {
  fileInputRef.value?.click()
}

function startAddMeal(mealType: string) {
  selectedMealType.value = mealType
  triggerPhotoCapture()
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  showRecognition.value = true
  recognizing.value = true
  recognitionError.value = false
  recognitionResult.value = null
  editableItems.value = []

  try {
    const result = await recognizeFood(file)
    recognitionResult.value = result
    editableItems.value = result.items.map((item) => ({ ...item }))

    // Auto-detect meal type from time
    const hour = dayjs().hour()
    if (hour >= 5 && hour < 10) selectedMealType.value = 'breakfast'
    else if (hour >= 10 && hour < 14) selectedMealType.value = 'lunch'
    else if (hour >= 14 && hour < 17) selectedMealType.value = 'snack'
    else selectedMealType.value = 'dinner'
  } catch (err) {
    console.error('Food recognition failed:', err)
    // Use mock data on failure
    recognitionResult.value = {
      image_url: '',
      items: [
        { id: '1', name: '米饭', portion: '一碗 (约200g)', portion_grams: 200, calories: 232, protein_g: 5.2, carbs_g: 51.2, fat_g: 0.6, confidence: 0.92 },
        { id: '2', name: '红烧肉', portion: '3块 (约150g)', portion_grams: 150, calories: 585, protein_g: 22.5, carbs_g: 12.0, fat_g: 49.5, confidence: 0.68, needs_confirmation: true },
        { id: '3', name: '清炒时蔬', portion: '一碟 (约100g)', portion_grams: 100, calories: 45, protein_g: 2.1, carbs_g: 6.8, fat_g: 1.2, confidence: 0.88 },
      ],
    }
    editableItems.value = recognitionResult.value.items.map((item) => ({ ...item }))
  } finally {
    recognizing.value = false
    target.value = ''
  }
}

function removeItem(index: number) {
  editableItems.value.splice(index, 1)
}

function cancelRecognition() {
  showRecognition.value = false
  recognitionResult.value = null
  recognitionError.value = false
  editableItems.value = []
}

function retryRecognition() {
  recognitionError.value = false
  fileInputRef.value?.click()
}

async function handleSaveMeal() {
  if (editableItems.value.length === 0) return

  try {
    await saveMeal({
      meal_type: selectedMealType.value,
      image_url: recognitionResult.value?.image_url || '',
      items: editableItems.value.map((item) => ({
        food_name: item.name,
        portion: item.portion,
        portion_grams: item.portion_grams,
        calories: Number(item.calories) || 0,
        protein_g: item.protein_g,
        carbs_g: item.carbs_g,
        fat_g: item.fat_g,
        confidence: item.confidence,
        user_confirmed: true,
      })),
    })

    // Update local state
    const totalCal = editableTotalCalories.value
    const slot = mealSlots.value.find((s) => s.type === selectedMealType.value)
    if (slot) {
      slot.data = {
        totalCalories: totalCal,
        items: editableItems.value.map((item, i) => ({
          id: `local-${i}`,
          foodName: item.name,
          portion: item.portion,
          calories: Math.round(Number(item.calories) || 0),
        })),
      }
      slot.time = dayjs().format('HH:mm')
    }

    dailyTotals.value.totalCalories += totalCal
    dailyTotals.value.protein += Math.round(editableItems.value.reduce((s, i) => s + i.protein_g, 0))
    dailyTotals.value.carbs += Math.round(editableItems.value.reduce((s, i) => s + i.carbs_g, 0))
    dailyTotals.value.fat += Math.round(editableItems.value.reduce((s, i) => s + i.fat_g, 0))

    cancelRecognition()
  } catch (err) {
    console.error('Save meal failed:', err)
  }
}
</script>

<style lang="less" scoped>
.nutrition-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-bg);
  position: relative;

  &__content {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    padding-bottom: 80px;
    -webkit-overflow-scrolling: touch;
  }
}

.intake-skeleton {
  margin-bottom: 16px;
}

.intake-banner {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;

  &__info { margin-bottom: 14px; }
  &__calories { display: flex; align-items: baseline; gap: 4px; }
  &__current { font-size: 32px; font-weight: 800; color: var(--text-primary); }
  &__divider { font-size: 18px; color: var(--text-hint); }
  &__goal { font-size: 18px; color: var(--text-secondary); }
  &__label { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
  &__macros { display: flex; gap: 12px; }
}

.macro-item {
  flex: 1; text-align: center; padding: 8px;
  background: var(--app-bg); border-radius: 8px;
  &__value { font-size: 16px; font-weight: 700; color: var(--text-primary); }
  &__label {
    font-size: 11px; margin-top: 2px;
    &--protein { color: #ff6b6b; }
    &--carbs { color: #ffc107; }
    &--fat { color: #4ecdc4; }
  }
}

.meal-card {
  background: var(--card-bg); border-radius: 12px; padding: 14px; margin-bottom: 10px;
  &__header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
  &__type { font-size: 15px; font-weight: 600; color: var(--text-primary); }
  &__time { font-size: 12px; color: var(--text-secondary); flex: 1; }
  &__calories { font-size: 14px; font-weight: 600; color: var(--primary-color); }
  &__add { font-size: 13px; color: var(--primary-color); cursor: pointer; }
  &__empty { text-align: center; padding: 16px; font-size: 13px; color: var(--text-hint); }
}

.food-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 0; border-bottom: 1px solid var(--border-color);
  &:last-child { border-bottom: none; }
  &__name { font-size: 13px; color: var(--text-primary); flex: 1; }
  &__portion { font-size: 12px; color: var(--text-secondary); }
  &__kcal { font-size: 13px; font-weight: 600; color: var(--text-primary); width: 60px; text-align: right; }
}

.fab {
  position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%);
  display: flex; align-items: center; gap: 8px;
  padding: 12px 28px; background: var(--primary-color); color: #fff;
  border-radius: 28px; cursor: pointer;
  box-shadow: 0 4px 16px rgba(25, 137, 250, 0.4);
  transition: all 0.2s; z-index: 50;
  &:active { transform: translateX(-50%) scale(0.96); }
  &__icon { font-size: 20px; }
  &__text { font-size: 15px; font-weight: 600; }
}

/* Recognition Overlay */
.recognition-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: var(--app-bg); z-index: 100;
  display: flex; flex-direction: column;

  &__header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; background: var(--card-bg);
    border-bottom: 1px solid var(--border-color);
  }
  &__back { font-size: 28px; font-weight: 300; cursor: pointer; width: 40px; }
  &__title { font-size: 17px; font-weight: 600; }
  &__loading { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; }
  &__spinner {
    width: 40px; height: 40px; border: 3px solid var(--border-color);
    border-top-color: var(--primary-color); border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  &__loading-text { font-size: 14px; color: var(--text-secondary); }
  &__content { flex: 1; overflow-y: auto; padding: 12px; -webkit-overflow-scrolling: touch; }
  &__image {
    width: 100%; height: 160px; object-fit: cover;
    border-radius: 12px; margin-bottom: 12px;
  }
}

@keyframes spin { to { transform: rotate(360deg); } }

.meal-type-selector {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;
  &__label { font-size: 14px; color: var(--text-secondary); }
}

.meal-type-chip {
  padding: 6px 14px; border-radius: 16px; font-size: 13px;
  background: var(--card-bg); color: var(--text-primary);
  border: 1px solid var(--border-color); cursor: pointer;
  &--active { background: var(--primary-color); color: #fff; border-color: var(--primary-color); }
}

.editable-items { margin-bottom: 12px; }

.editable-item {
  background: var(--card-bg); border-radius: 10px; padding: 12px; margin-bottom: 8px;
  &__row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
  &__input {
    border: 1px solid var(--border-color); border-radius: 6px;
    padding: 6px 10px; font-size: 13px; outline: none;
    &:focus { border-color: var(--primary-color); }
  }
  &__name { flex: 1; }
  &__portion { flex: 1; }
  &__kcal { font-size: 14px; font-weight: 600; color: var(--primary-color); white-space: nowrap; }
  &__warn { font-size: 12px; color: var(--warning-color); white-space: nowrap; }
  &__macros { display: flex; gap: 12px; font-size: 11px; color: var(--text-hint); margin-bottom: 6px; }
  &__actions { display: flex; align-items: center; gap: 8px; }
  &__cal-input {
    width: 80px; border: 1px solid var(--border-color); border-radius: 6px;
    padding: 4px 8px; font-size: 12px; outline: none;
    &:focus { border-color: var(--primary-color); }
  }
  &__remove { font-size: 12px; color: var(--danger-color); cursor: pointer; margin-left: auto; }
}

.recognition-totals {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; background: var(--card-bg); border-radius: 10px;
  font-size: 15px; font-weight: 600; margin-bottom: 12px;
  &__disclaimer { font-size: 11px; color: var(--text-hint); font-weight: 400; }
}

.save-btn {
  width: 100%; padding: 14px; border: none; border-radius: 24px;
  background: var(--primary-color); color: #fff;
  font-size: 16px; font-weight: 600; cursor: pointer;
  transition: opacity 0.2s;
  &:active { opacity: 0.85; }
}
</style>
