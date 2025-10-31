import React, { useState } from 'react'
import { Star, MessageSquare, BarChart3, FileText, StarOff } from 'lucide-react'
import { Button } from './ui/Button'
import { formatRelativeTime } from '@/lib/utils'
import { Chat, Artifact } from '@/types'

interface StarredItem {
  id: string
  type: 'chat' | 'artifact'
  title: string
  description?: string
  createdAt: Date
  data: Chat | Artifact
}

interface StarredPageProps {
  chats: Chat[]
  onSelectChat: (chatId: string) => void
}

export const StarredPage: React.FC<StarredPageProps> = ({ chats, onSelectChat }) => {
  // In a real app, this would come from storage/API
  const [starredItems, setStarredItems] = useState<StarredItem[]>([])

  const toggleStar = (item: StarredItem) => {
    if (starredItems.find((i) => i.id === item.id)) {
      setStarredItems(starredItems.filter((i) => i.id !== item.id))
    } else {
      setStarredItems([...starredItems, item])
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'artifact':
        return <BarChart3 className="w-5 h-5" />
      case 'chat':
        return <MessageSquare className="w-5 h-5" />
      default:
        return <FileText className="w-5 h-5" />
    }
  }

  if (starredItems.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <Star className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Starred Items</h3>
            <p className="text-gray-500 mb-4">
              Star chats or artifacts to save them here for quick access.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">Starred</h1>
          <p className="text-gray-600">Your saved chats and artifacts</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {starredItems.map((item) => (
            <div
              key={item.id}
              className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3 flex-1">
                  <div className="text-veeam">{getIcon(item.type)}</div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 truncate">{item.title}</h3>
                    {item.description && (
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {item.description}
                      </p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => toggleStar(item)}
                  className="text-yellow-500 hover:text-yellow-600 p-1"
                  title="Unstar"
                >
                  <Star className="w-5 h-5 fill-current" />
                </button>
              </div>

              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                <span className="text-xs text-gray-500">
                  {formatRelativeTime(item.createdAt)}
                </span>
                {item.type === 'chat' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onSelectChat(item.data.id)}
                  >
                    Open
                  </Button>
                )}
                {item.type === 'artifact' && (
                  <Button variant="ghost" size="sm">
                    View
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

