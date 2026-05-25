import apiClient from './client'

export interface HealthMetrics {
  steps: number
  heartRate: number
  sleepMinutes: number
  caloriesBurned: number
  exerciseMinutes: number
  weight: number
}

export interface DietSummary {
  totalCalories: number
  goalCalories: number
  protein: number
  carbs: number
  fat: number
  meals: MealEntry[]
}

export interface MealEntry {
  id: string
  mealType: string
  imageUrl?: string
  totalCalories: number
  items: FoodItem[]
  recordDate: string
  confirmed: boolean
}

export interface FoodItem {
  id: string
  foodName: string
  portion: string
  portionGrams: number
  calories: number
  proteinG: number
  carbsG: number
  fatG: number
  confidence: number
  userConfirmed: boolean
}

export function getTodayHealthMetrics(): Promise<HealthMetrics> {
  return apiClient.get('/health/metrics')
}

export function getTodayDietSummary(): Promise<DietSummary> {
  return apiClient.get('/health/diet/today')
}

export function confirmDietRecord(recordId: string): Promise<void> {
  return apiClient.put(`/health/diet/${recordId}/confirm`)
}
