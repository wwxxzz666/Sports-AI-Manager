import apiClient from './client'

export interface RatingDimensions {
  strength: number
  endurance: number
  flexibility: number
  consistency: number
  nutrition: number
}

export interface CurrentRating {
  id: string
  composite_score: number
  tier: string
  percentile: number
  dimensions: RatingDimensions
  rating_date: string
}

export interface RatingHistoryItem {
  id: string
  score: number
  tier: string
  date: string
  delta: number
}

export function generateRating(): Promise<CurrentRating> {
  return apiClient.post('/ratings/generate', {})
}

export function getCurrentRating(): Promise<CurrentRating | null> {
  return apiClient.get('/ratings/current')
}

export function getRatingHistory(): Promise<RatingHistoryItem[]> {
  return apiClient.get('/ratings/history')
}
