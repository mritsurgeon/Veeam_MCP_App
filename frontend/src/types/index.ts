export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  toolCalls?: ToolCall[]
}

export interface ToolCall {
  id: string
  name: string
  arguments: Record<string, any>
}

export interface Chat {
  id: string
  title: string
  createdAt: Date
  updatedAt: Date
  messages: Message[]
}

export interface Artifact {
  id: string
  title: string
  type: 'report' | 'dashboard' | 'table' | 'script' | 'diagram'
  content: string
  preview?: string
  code?: string
  metadata?: Record<string, any>
}

export interface LLMProvider {
  id: string
  name: string
  models: string[]
}

