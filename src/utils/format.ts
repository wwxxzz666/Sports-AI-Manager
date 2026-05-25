import dayjs from 'dayjs'

export function formatGreeting(): string {
  const hour = dayjs().hour()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
}

export function formatDate(date?: Date): string {
  return dayjs(date).format('YYYY年M月D日 dddd')
}

export function formatNumber(num: number): string {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

export function formatCalories(kcal: number): string {
  return `${Math.round(kcal)} kcal`
}

export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 9)
}
