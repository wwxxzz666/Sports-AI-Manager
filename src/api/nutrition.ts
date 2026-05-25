import apiClient from './client'

export interface FoodRecognitionItem {
  id: string
  name: string
  portion: string
  portion_grams: number
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  confidence: number
  needs_confirmation?: boolean
}

export interface FoodRecognitionResult {
  image_url: string
  items: FoodRecognitionItem[]
  total_calories: number
  total_protein: number
  total_carbs: number
  total_fat: number
  disclaimer: string
}

export interface SaveMealItem {
  food_name: string
  portion: string
  portion_grams: number
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  confidence: number
  user_confirmed: boolean
}

export interface SaveMealRequest {
  meal_type: string
  image_url: string
  items: SaveMealItem[]
  record_date?: string
}

export interface SaveMealResponse {
  id: string
  meal_type: string
  total_calories: number
  items_count: number
  record_date: string
}

export function recognizeFood(file: File): Promise<FoodRecognitionResult> {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/nutrition/recognize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })
}

export function saveMeal(data: SaveMealRequest): Promise<SaveMealResponse> {
  return apiClient.post('/nutrition/meal', data)
}

export function deleteMeal(recordId: string): Promise<void> {
  return apiClient.delete(`/nutrition/meal/${recordId}`)
}
