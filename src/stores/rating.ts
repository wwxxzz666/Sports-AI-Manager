import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface RatingData {
  compositeScore: number
  tier: string
  percentile: number
  dimensions: {
    strength: number
    endurance: number
    flexibility: number
    balance: number
    recovery: number
  }
}

export interface RatingHistory {
  id: string
  score: number
  tier: string
  date: string
}

export const useRatingStore = defineStore('rating', () => {
  const currentRating = ref<RatingData | null>(null)
  const history = ref<RatingHistory[]>([])
  const loading = ref(false)

  function setCurrentRating(data: RatingData) {
    currentRating.value = data
  }

  function setHistory(data: RatingHistory[]) {
    history.value = data
  }

  return {
    currentRating,
    history,
    loading,
    setCurrentRating,
    setHistory,
  }
})
