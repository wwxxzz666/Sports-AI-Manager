import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FoodItem, MealEntry } from '@/api/health'

export const useNutritionStore = defineStore('nutrition', () => {
  const meals = ref<MealEntry[]>([])
  const recognitionResult = ref<FoodItem[]>([])
  const dailyTotals = ref({
    totalCalories: 0,
    goalCalories: 2200,
    protein: 0,
    carbs: 0,
    fat: 0,
  })
  const selectedMealType = ref<string>('lunch')
  const loading = ref(false)

  function setRecognitionResult(items: FoodItem[]) {
    recognitionResult.value = items
  }

  function updateFoodItem(itemId: string, updates: Partial<FoodItem>) {
    const item = recognitionResult.value.find((i) => i.id === itemId)
    if (item) {
      Object.assign(item, updates)
    }
  }

  function saveMeal(meal: MealEntry) {
    meals.value.push(meal)
    dailyTotals.value.totalCalories += meal.totalCalories
    meal.items.forEach((item) => {
      dailyTotals.value.protein += item.proteinG
      dailyTotals.value.carbs += item.carbsG
      dailyTotals.value.fat += item.fatG
    })
    recognitionResult.value = []
  }

  function setDailyTotals(totals: typeof dailyTotals.value) {
    dailyTotals.value = totals
  }

  function setSelectedMealType(type: string) {
    selectedMealType.value = type
  }

  return {
    meals,
    recognitionResult,
    dailyTotals,
    selectedMealType,
    loading,
    setRecognitionResult,
    updateFoodItem,
    saveMeal,
    setDailyTotals,
    setSelectedMealType,
  }
})
