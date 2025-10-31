import React from 'react'
import { MessageSquare, Wrench, Star, Plus, Clock, Trash2 } from 'lucide-react'
import { Button } from './ui/Button'
import { cn, formatRelativeTime } from '@/lib/utils'
import { Chat } from '@/types'

interface SidebarProps {
  chats: Chat[]
  activeChatId?: string
  activeNav: 'chats' | 'tools' | 'starred'
  onNewChat: () => void
  onSelectChat: (chatId: string) => void
  onDeleteChat: (chatId: string) => void
  onNavChange: (nav: 'chats' | 'tools' | 'starred') => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  chats,
  activeChatId,
  activeNav,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onNavChange,
}) => {

  const navigation = [
    { id: 'chats' as const, label: 'Chats', icon: MessageSquare },
    { id: 'tools' as const, label: 'Tools', icon: Wrench },
    { id: 'starred' as const, label: 'Starred', icon: Star },
  ]

  return (
    <div className="w-64 h-screen bg-white border-r border-gray-200 flex flex-col">
      {/* Header with Branding */}
      <div className="px-4 pt-6 pb-4 border-b border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          {/* Veeam badge with arrow */}
          <div className="relative bg-veeam rounded-md px-3 py-1.5 flex items-center">
            <span className="text-white text-sm font-semibold">veeam</span>
            <div className="absolute right-0 top-1/2 translate-x-1/2 -translate-y-1/2 w-0 h-0 border-t-[8px] border-t-transparent border-b-[8px] border-b-transparent border-l-[6px] border-l-veeam"></div>
          </div>
          <div className="flex items-baseline">
            <span className="font-bold text-gray-900 text-sm">MCP Chat</span>
            <span className="text-xs text-gray-500 ml-1">Client</span>
          </div>
        </div>
        {/* Start New Chat Button */}
        <Button
          onClick={onNewChat}
          className="w-full bg-veeam hover:bg-veeam-dark text-white h-11 rounded-lg font-medium shadow-sm"
          size="md"
        >
          <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center mr-2">
            <Plus className="w-4 h-4 text-white" />
          </div>
          Start new chat
        </Button>
      </div>

      {/* Navigation */}
      <nav className="px-3 py-2">
        {navigation.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              onClick={() => onNavChange(item.id)}
              className={cn(
                'w-full flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                activeNav === item.id
                  ? 'bg-veeam-light text-veeam-dark font-semibold'
                  : 'text-gray-700 hover:bg-gray-50'
              )}
            >
              <Icon className="w-4 h-4 mr-3" />
              {item.label}
            </button>
          )
        })}
      </nav>

      {/* Recent Chats - Only show when on chats navigation */}
      {activeNav === 'chats' && (
        <div className="flex-1 overflow-y-auto">
          <div className="px-4 py-3 flex items-center text-xs font-semibold text-gray-500 uppercase tracking-wider border-t border-gray-100 mt-2">
            <Clock className="w-3.5 h-3.5 mr-2" />
            Recent
          </div>
          <div className="px-2">
            {chats.length === 0 ? (
              <div className="px-3 py-8 text-center text-sm text-gray-500">
                No recent chats
              </div>
            ) : (
              chats.map((chat) => (
            <div
              key={chat.id}
              className={cn(
                'group flex items-center mb-1 rounded-md',
                activeChatId === chat.id && 'bg-veeam-light'
              )}
            >
              <button
                onClick={() => onSelectChat(chat.id)}
                className={cn(
                  'flex-1 flex items-start px-3 py-2.5 rounded-lg text-sm transition-all text-left',
                  activeChatId === chat.id
                    ? 'bg-veeam-light text-veeam-dark'
                    : 'text-gray-700 hover:bg-gray-50'
                )}
              >
                <MessageSquare className="w-4 h-4 mr-3 mt-0.5 flex-shrink-0 text-gray-500" />
                <div className="flex-1 min-w-0">
                  <div className="truncate font-medium text-gray-900">{chat.title}</div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {formatRelativeTime(chat.updatedAt)}
                  </div>
                </div>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  if (confirm('Delete this chat?')) {
                    onDeleteChat(chat.id)
                  }
                }}
                className="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-600 transition-opacity"
                title="Delete chat"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Empty state for tools/starred views */}
      {activeNav !== 'chats' && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-sm text-gray-500 px-4">
            {activeNav === 'tools' && 'Use the Tools page to manage MCP tools'}
            {activeNav === 'starred' && 'Star items to see them here'}
          </div>
        </div>
      )}
    </div>
  )
}

