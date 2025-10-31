import React, { useState, useRef, useEffect } from 'react'
import { Send, HelpCircle, AlertCircle, Settings } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { ChatMessage } from './ChatMessage'
import { Message, Artifact } from '@/types'
import { chatAPI } from '@/services/api'

interface ChatInterfaceProps {
  messages: Message[]
  provider: string
  model: string
  onNewMessage: (message: Message) => void
  onArtifactGenerated?: (artifact: Artifact) => void
  onOpenSettings?: () => void
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  provider,
  model,
  onNewMessage,
  onArtifactGenerated,
  onOpenSettings,
}) => {
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingContent])

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    onNewMessage(userMessage)
    setInput('')
    setIsStreaming(true)
    setStreamingContent('')

    const allMessages = [...messages, userMessage]

    try {
      // Clear any previous errors
      setError(null)

      // For now, use non-streaming - streaming will be implemented with proper SSE endpoint
      const response = await chatAPI.sendMessage({
        provider,
        messages: allMessages.map((m) => ({
          role: m.role,
          content: m.content,
        })),
        model,
        stream: false,
      })

      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
      }
      onNewMessage(assistantMessage)

      // Check if response contains artifact indicators
      if (response.content.includes('Dashboard') || response.content.includes('Report')) {
        const artifactType = response.content.includes('Dashboard') ? 'dashboard' : 'report'
        onArtifactGenerated?.({
          id: `artifact-${Date.now()}`,
          title: response.content.includes('Dashboard')
            ? 'Veeam Backup Dashboard'
            : 'Executive Backup Report',
          type: artifactType,
          content: response.content,
          preview: response.content,
        })
      }
    } catch (error: any) {
      console.error('Error sending message:', error)
      
      // Check if error is related to missing API key
      const errorMessage = error?.response?.data?.detail || error?.message || String(error)
      
      if (
        errorMessage.toLowerCase().includes('api key') ||
        errorMessage.toLowerCase().includes('authentication') ||
        errorMessage.toLowerCase().includes('unauthorized') ||
        errorMessage.toLowerCase().includes('key is required')
      ) {
        setError('API key not configured. Please configure your API key in Settings.')
      } else {
        setError(`Error: ${errorMessage}`)
      }
    } finally {
      setIsStreaming(false)
      setStreamingContent('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-50 relative">
      {/* Messages Container */}
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto px-8 py-6 space-y-6"
      >
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isStreaming && streamingContent && (
          <ChatMessage
            message={{
              id: 'streaming',
              role: 'assistant',
              content: streamingContent,
              timestamp: new Date(),
            }}
          />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mx-8 mb-4 p-4 bg-red-50 border border-red-200 rounded-xl shadow-sm">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-900">{error}</p>
              {error.includes('API key') && onOpenSettings && (
                <button
                  onClick={onOpenSettings}
                  className="mt-2 text-sm text-red-700 hover:text-red-900 underline flex items-center space-x-1"
                >
                  <Settings className="w-4 h-4" />
                  <span>Open Settings</span>
                </button>
              )}
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-600 hover:text-red-800 font-bold text-lg"
            >
              <span className="sr-only">Dismiss</span>
              ×
            </button>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex items-end space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Shift + Enter for new line)"
            className="flex-1 min-h-[60px] max-h-32 px-4 py-3 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-veeam focus:border-transparent bg-white"
            disabled={isStreaming}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            className="bg-veeam hover:bg-veeam-dark text-white h-[60px] px-5 rounded-xl shadow-sm"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>

        {/* Tool Output Section */}
        <div className="mt-3 px-2 text-xs text-gray-400 font-mono">
          &lt;&gt; Tool Output
        </div>

      </div>

      {/* Help Button - Fixed position */}
      <div className="absolute bottom-6 right-6 z-10">
        <Button variant="ghost" size="sm" className="rounded-full w-9 h-9 p-0 bg-gray-100 hover:bg-gray-200 shadow-sm">
          <HelpCircle className="w-4 h-4 text-gray-600" />
        </Button>
      </div>
    </div>
  )
}

