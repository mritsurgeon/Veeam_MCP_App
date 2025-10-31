import React, { useState, useEffect } from 'react'
import { Sidebar } from './components/Sidebar'
import { Header } from './components/Header'
import { ChatInterface } from './components/ChatInterface'
import { ArtifactViewer } from './components/ArtifactViewer'
import { Settings } from './components/Settings'
import { ToolsPage } from './components/ToolsPage'
import { StarredPage } from './components/StarredPage'
import { Chat, Message, Artifact } from './types'
import { chatAPI } from './services/api'

// Mock recent chats - in production, this would come from storage/API
const initialChats: Chat[] = [
  {
    id: '1',
    title: 'Veeam Backup Configuration',
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    messages: [],
  },
  {
    id: '2',
    title: 'Repository Storage Capacity',
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
    messages: [],
  },
  {
    id: '3',
    title: 'Restore Point Configuration',
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    messages: [],
  },
  {
    id: '4',
    title: 'Cloud Connect Setup',
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    messages: [],
  },
  {
    id: '5',
    title: 'Replication Job Troubleshooting',
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    messages: [],
  },
]

const App: React.FC = () => {
  const [chats, setChats] = useState<Chat[]>(initialChats)
  const [activeChatId, setActiveChatId] = useState<string | undefined>(undefined)
  const [currentChat, setCurrentChat] = useState<Chat | null>(null)
  const [selectedProvider, setSelectedProvider] = useState('openai')
  const [selectedModel, setSelectedModel] = useState('gpt-4')
  const [availableProviders, setAvailableProviders] = useState<string[]>([])
  const [artifact, setArtifact] = useState<Artifact | null>(null)
  const [darkMode, setDarkMode] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [availableModels, setAvailableModels] = useState<Array<{ value: string; label: string; provider: string; healthy: boolean }>>([])
  const [activeNav, setActiveNav] = useState<'chats' | 'tools' | 'starred'>('chats')

  useEffect(() => {
    // Load providers
    chatAPI
      .getProviders()
      .then((providers) => {
        setAvailableProviders(providers)
        if (providers.length > 0 && !selectedProvider) {
          setSelectedProvider(providers[0])
        }
      })
      .catch(console.error)
    
    // Load available models from all providers
    loadAvailableModels()
  }, [])

  const loadAvailableModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/settings/providers/status')
      const statuses = await response.json()
      
      const models: Array<{ value: string; label: string; provider: string; healthy: boolean }> = []
      
      statuses.forEach((status: any) => {
        if (status.configured && status.healthy && status.available_models.length > 0) {
          status.available_models.forEach((model: string) => {
            const providerName = status.provider === 'openai' ? 'OpenAI' :
                               status.provider === 'anthropic' ? 'Anthropic' :
                               status.provider === 'gemini' ? 'Gemini' :
                               status.provider === 'ollama' ? 'Ollama' : status.provider
            models.push({
              value: model,
              label: `${providerName} ${model}`,
              provider: status.provider,
              healthy: status.healthy,
            })
          })
        }
      })

      // Fallback to default models if none available
      if (models.length === 0) {
        const defaultModels = [
          { value: 'gpt-4', label: 'OpenAI GPT-4', provider: 'openai', healthy: false },
          { value: 'gpt-4-turbo', label: 'OpenAI GPT-4 Turbo', provider: 'openai', healthy: false },
          { value: 'gpt-3.5-turbo', label: 'OpenAI GPT-3.5 Turbo', provider: 'openai', healthy: false },
          { value: 'claude-3-5-sonnet-20241022', label: 'Anthropic Claude 3.5 Sonnet', provider: 'anthropic', healthy: false },
          { value: 'claude-3-opus-20240229', label: 'Anthropic Claude 3 Opus', provider: 'anthropic', healthy: false },
          { value: 'gemini-pro', label: 'Gemini Pro', provider: 'gemini', healthy: false },
          { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro', provider: 'gemini', healthy: false },
        ]
        setAvailableModels(defaultModels)
      } else {
        setAvailableModels(models)
        // Auto-select first healthy model
        const firstHealthy = models.find(m => m.healthy)
        if (firstHealthy && !selectedModel) {
          setSelectedModel(firstHealthy.value)
          setSelectedProvider(firstHealthy.provider)
        }
      }
    } catch (error) {
      console.error('Error loading available models:', error)
    }
  }

  // Models are loaded dynamically from availableModels state
  const models = availableModels.length > 0 
    ? availableModels 
    : [
        { value: 'gpt-4', label: 'OpenAI GPT-4', provider: 'openai', healthy: false },
        { value: 'gpt-4-turbo', label: 'OpenAI GPT-4 Turbo', provider: 'openai', healthy: false },
      ]

  const handleNewChat = () => {
    const newChat: Chat = {
      id: `chat-${Date.now()}`,
      title: 'New Chat',
      createdAt: new Date(),
      updatedAt: new Date(),
      messages: [],
    }
    setChats([newChat, ...chats])
    setActiveChatId(newChat.id)
    setCurrentChat(newChat)
    setArtifact(null)
  }

  const handleSelectChat = (chatId: string) => {
    setActiveChatId(chatId)
    const chat = chats.find((c) => c.id === chatId)
    setCurrentChat(chat || null)
    setArtifact(null)
    setActiveNav('chats') // Switch to chats view when selecting a chat
  }

  const handleDeleteChat = (chatId: string) => {
    setChats(chats.filter((c) => c.id !== chatId))
    if (activeChatId === chatId) {
      setActiveChatId(undefined)
      setCurrentChat(null)
    }
  }

  const handleNewMessage = (message: Message) => {
    if (!currentChat) return

    const updatedChat: Chat = {
      ...currentChat,
      messages: [...currentChat.messages, message],
      updatedAt: new Date(),
      title:
        currentChat.title === 'New Chat' && message.role === 'user'
          ? message.content.substring(0, 50) + (message.content.length > 50 ? '...' : '')
          : currentChat.title,
    }

    setCurrentChat(updatedChat)
    setChats(chats.map((c) => (c.id === updatedChat.id ? updatedChat : c)))
  }

  const handleArtifactGenerated = (newArtifact: Artifact) => {
    setArtifact(newArtifact)
  }

  const messages = currentChat?.messages || []

  return (
    <div className={`h-screen flex bg-gray-50 ${darkMode ? 'dark' : ''}`}>
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        activeNav={activeNav}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        onNavChange={setActiveNav}
      />

      <div className="flex-1 flex flex-col bg-white">
        <Header
          selectedModel={selectedModel}
          models={models}
          onModelChange={(model) => {
            setSelectedModel(model)
            // Find provider for this model
            const modelInfo = models.find(m => m.value === model)
            if (modelInfo) {
              setSelectedProvider(modelInfo.provider)
            }
          }}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode(!darkMode)}
          onSettings={() => setShowSettings(true)}
          onRefresh={loadAvailableModels}
        />

        <div className="flex-1 flex overflow-hidden">
          {activeNav === 'chats' && (
            <>
              <ChatInterface
                messages={messages}
                provider={selectedProvider}
                model={selectedModel}
                onNewMessage={handleNewMessage}
                onArtifactGenerated={handleArtifactGenerated}
                onOpenSettings={() => setShowSettings(true)}
              />

              {artifact && (
                <ArtifactViewer
                  artifact={artifact}
                  onClose={() => setArtifact(null)}
                  onExport={(id) => console.log('Export artifact:', id)}
                />
              )}
            </>
          )}

          {activeNav === 'tools' && <ToolsPage />}

          {activeNav === 'starred' && (
            <StarredPage chats={chats} onSelectChat={handleSelectChat} />
          )}
        </div>
      </div>

      <Settings
        isOpen={showSettings}
        onClose={() => {
          setShowSettings(false)
          loadAvailableModels() // Refresh models after closing settings
        }}
      />
    </div>
  )
}

export default App

