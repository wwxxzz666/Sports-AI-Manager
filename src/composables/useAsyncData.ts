import { ref, type Ref } from 'vue'

interface UseAsyncDataReturn<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  execute: (fetcher: () => Promise<T>) => Promise<void>
  reset: () => void
}

export function useAsyncData<T = unknown>(): UseAsyncDataReturn<T> {
  const data = ref<T | null>(null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function execute(fetcher: () => Promise<T>) {
    loading.value = true
    error.value = null
    try {
      data.value = await fetcher()
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '请求失败'
      error.value = msg
    } finally {
      loading.value = false
    }
  }

  function reset() {
    data.value = null
    loading.value = false
    error.value = null
  }

  return { data, loading, error, execute, reset }
}
