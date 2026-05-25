import apiClient from './client'

export interface MotionAnalysisResult {
  record_id: string
  video_url: string
  sport_type: string
  overall_score: number
  posture_issues: string[]
  suggestions: string[]
  risks: string[]
  recommended_training: string[]
  summary: string
  disclaimer: string
}

export interface MotionHistoryItem {
  id: string
  sport_type: string
  video_url: string
  analysis: {
    overall_score?: number
    posture_issues?: string[]
    suggestions?: string[]
    risks?: string[]
    recommended_training?: string[]
    summary?: string
  } | null
  notes: string
  date: string
}

export function analyzeMotion(
  file: File,
  sportType: string,
  goal?: string
): Promise<MotionAnalysisResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('sport_type', sportType)
  if (goal) {
    formData.append('goal', goal)
  }
  return apiClient.post('/motion/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}

export function getMotionHistory(): Promise<MotionHistoryItem[]> {
  return apiClient.get('/motion/history')
}
