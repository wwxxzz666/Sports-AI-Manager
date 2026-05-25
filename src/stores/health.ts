import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { HealthMetrics, DietSummary } from '@/api/health'

export const useHealthStore = defineStore('health', () => {
  const todayMetrics = ref<HealthMetrics | null>(null)
  const weeklyMetrics = ref<HealthMetrics | null>(null)
  const dietSummary = ref<DietSummary | null>(null)
  const selectedPeriod = ref<'today' | 'weekly'>('today')
  const loading = ref(false)

  function setMetrics(period: 'today' | 'weekly', data: HealthMetrics) {
    if (period === 'today') {
      todayMetrics.value = data
    } else {
      weeklyMetrics.value = data
    }
  }

  function setDietSummary(data: DietSummary) {
    dietSummary.value = data
  }

  function setPeriod(period: 'today' | 'weekly') {
    selectedPeriod.value = period
  }

  return {
    todayMetrics,
    weeklyMetrics,
    dietSummary,
    selectedPeriod,
    loading,
    setMetrics,
    setDietSummary,
    setPeriod,
  }
})
