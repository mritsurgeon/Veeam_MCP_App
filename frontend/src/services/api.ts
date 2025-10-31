import axios from 'axios'
import { Message } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ChatRequest {
  provider: string
  messages: Message[]
  model?: string
  stream?: boolean
}

export interface ChatResponse {
  content: string
  model: string
  finish_reason?: string
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  tool_calls?: any[]
}

export const chatAPI = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>('/api/v1/chat', request)
      return response.data
    } catch (error: any) {
      // Re-throw with better error information
      if (error.response) {
        // Server responded with error
        throw {
          response: {
            data: {
              detail: error.response.data?.detail || error.response.data?.message || 'An error occurred'
            }
          },
          message: error.response.data?.detail || error.response.data?.message || 'An error occurred'
        }
      } else if (error.request) {
        // Request made but no response
        throw {
          message: 'No response from server. Please check your connection.'
        }
      } else {
        // Something else happened
        throw error
      }
    }
  },

  async streamMessage(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    const eventSource = new EventSource(
      `${API_BASE_URL}/api/v1/chat?provider=${request.provider}&stream=true`
    )

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.content) {
          onChunk(data.content)
        }
        if (data.finished) {
          onComplete()
          eventSource.close()
        }
      } catch (error) {
        onError(error as Error)
        eventSource.close()
      }
    }

    eventSource.onerror = (error) => {
      onError(new Error('Stream connection failed'))
      eventSource.close()
    }
  },

  async getProviders(): Promise<string[]> {
    const response = await api.get<{ providers: string[] }>('/api/v1/providers')
    return response.data.providers
  },

  async checkHealth(provider: string): Promise<boolean> {
    try {
      const response = await api.get(`/api/v1/providers/${provider}/health`)
      return response.data.healthy
    } catch {
      return false
    }
  },
}

