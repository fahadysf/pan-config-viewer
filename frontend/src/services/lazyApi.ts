import axios from 'axios'

const API_BASE_URL = ''

interface TaskResponse {
  task_id: string | null
  status: 'pending' | 'processing' | 'completed' | 'failed'
  message?: string
  data?: any
}

interface TaskStatus {
  task_id: string
  status: string
  progress: number
  created_at: string
  completed_at: string | null
  error: string | null
  has_data: boolean
}

export class LazyLoadingService {
  private pollingInterval = 500 // Start with 500ms
  private maxPollingInterval = 2000 // Max 2 seconds
  private maxRetries = 60 // Max 30 seconds with backoff

  /**
   * Fetch data with lazy loading and polling
   */
  async fetchWithLazyLoading<T>(
    endpoint: string,
    params: Record<string, any> = {},
    onProgress?: (progress: number) => void
  ): Promise<T> {
    try {
      // First, try the async endpoint
      const asyncEndpoint = endpoint.replace('/addresses', '/addresses/async')
      
      // Start async loading
      const startResponse = await axios.post(
        `${API_BASE_URL}${asyncEndpoint}`,
        null,
        { params }
      )

      const taskData: TaskResponse = startResponse.data

      // If data is immediately available (cached), return it
      if (taskData.status === 'completed' && taskData.data) {
        if (onProgress) onProgress(100)
        return taskData.data as T
      }

      // If we have a task_id, start polling
      if (taskData.task_id) {
        return await this.pollForResult<T>(taskData.task_id, onProgress)
      }

      throw new Error('No task ID received from server')
    } catch (error) {
      // Fallback to regular endpoint if async not available
      console.warn('Async endpoint failed, falling back to sync:', error)
      const response = await axios.get(`${API_BASE_URL}${endpoint}`, { params })
      return response.data
    }
  }

  /**
   * Poll for task completion
   */
  private async pollForResult<T>(
    taskId: string,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    let retries = 0
    let currentInterval = this.pollingInterval

    while (retries < this.maxRetries) {
      try {
        // Check task status
        const statusResponse = await axios.get(
          `${API_BASE_URL}/api/v1/tasks/${taskId}/status`
        )
        
        const status: TaskStatus = statusResponse.data

        // Update progress
        if (onProgress && status.progress) {
          onProgress(status.progress)
        }

        // Check if completed
        if (status.status === 'completed') {
          // Get the result
          const resultResponse = await axios.get(
            `${API_BASE_URL}/api/v1/tasks/${taskId}/result`
          )
          
          if (onProgress) onProgress(100)
          return resultResponse.data as T
        }

        // Check if failed
        if (status.status === 'failed') {
          throw new Error(status.error || 'Task failed')
        }

        // Wait before next poll with exponential backoff
        await new Promise(resolve => setTimeout(resolve, currentInterval))
        
        // Increase interval with backoff
        currentInterval = Math.min(currentInterval * 1.2, this.maxPollingInterval)
        retries++

      } catch (error: any) {
        if (error.response?.status === 404) {
          throw new Error('Task not found')
        }
        
        // For other errors, retry
        retries++
        
        if (retries >= this.maxRetries) {
          throw new Error('Polling timeout - task took too long')
        }

        await new Promise(resolve => setTimeout(resolve, currentInterval))
      }
    }

    throw new Error('Maximum polling retries exceeded')
  }

  /**
   * Check if lazy loading is available for an endpoint
   */
  async isLazyLoadingAvailable(endpoint: string): Promise<boolean> {
    try {
      const asyncEndpoint = endpoint.replace('/addresses', '/addresses/async')
      const response = await axios.options(`${API_BASE_URL}${asyncEndpoint}`)
      return response.status === 200
    } catch {
      return false
    }
  }
}

export const lazyLoadingService = new LazyLoadingService()