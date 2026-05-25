import apiClient from './client'

export function uploadImage(file: File): Promise<{ file_id: string; url: string; thumbnail_url: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/uploads/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function uploadVideo(file: File): Promise<{ file_id: string; url: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/uploads/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}
