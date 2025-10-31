import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { User, Bot, BarChart3 } from 'lucide-react'
import { formatTime } from '@/lib/utils'
import { Message } from '@/types'
import { Button } from './ui/Button'

interface ChatMessageProps {
  message: Message
  onViewArtifact?: (artifactId: string) => void
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, onViewArtifact }) => {
  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'

  // Extract artifact/view buttons from markdown
  const content = message.content
  const hasViewButton = content.includes('View Dashboard') || content.includes('View Report')

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`flex items-start space-x-3 max-w-3xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        {isAssistant && (
          <div className="flex-shrink-0 w-8 h-8 bg-veeam rounded-lg flex items-center justify-center">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
              />
            </svg>
          </div>
        )}
        {isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
            <User className="w-5 h-5 text-gray-600" />
          </div>
        )}

        {/* Message Bubble */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div
            className={`rounded-xl px-4 py-3 shadow-sm ${
              isUser
                ? 'bg-veeam text-white'
                : 'bg-white border border-gray-200 text-gray-900'
            }`}
          >
            {isAssistant ? (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                    strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                    code: ({ children }) => (
                      <code className="bg-gray-100 px-1 py-0.5 rounded text-sm">{children}</code>
                    ),
                  }}
                >
                  {content}
                </ReactMarkdown>
              </div>
            ) : (
              <p className="text-sm whitespace-pre-wrap">{content}</p>
            )}
          </div>

          {/* View Button (for artifacts) */}
          {isAssistant && hasViewButton && (
            <Button
              onClick={() => {
                // Extract artifact type from content
                const artifactType = content.includes('Dashboard') ? 'dashboard' : 'report'
                onViewArtifact?.(`artifact-${Date.now()}`)
              }}
              className="mt-3 bg-veeam hover:bg-veeam-dark text-white rounded-lg shadow-sm"
              size="sm"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              {content.includes('Dashboard') ? 'View Dashboard' : 'View Report'}
            </Button>
          )}

          {/* Timestamp */}
          <span className="text-xs text-gray-500 mt-1">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    </div>
  )
}

