import React from 'react'
import { Settings, Moon, RefreshCw } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select'
import { Button } from './ui/Button'

interface HeaderProps {
  selectedModel: string
  models: Array<{ value: string; label: string; provider?: string; healthy?: boolean }>
  onModelChange: (model: string) => void
  onSettings?: () => void
  onRefresh?: () => void
  darkMode?: boolean
  onToggleDarkMode?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  selectedModel,
  models,
  onModelChange,
  onSettings,
  onRefresh,
  darkMode = false,
  onToggleDarkMode,
}) => {
  return (
    <div className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-6">
      {/* Left: Branding */}
      <div className="flex items-center space-x-3">
        {/* Veeam Icon - Green square with circuit board icon */}
        <div className="w-8 h-8 bg-veeam rounded-lg flex items-center justify-center">
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
        <div className="flex items-baseline space-x-2">
          <span className="font-bold text-gray-900 text-base">MCP Chat</span>
          <span className="text-sm text-gray-500 font-normal">Client</span>
        </div>
        {/* Version badge */}
        <span className="ml-2 px-2 py-0.5 bg-veeam text-white text-xs font-medium rounded">
          v13
        </span>
      </div>

      {/* Right: Model selector and controls */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600 font-medium">Model:</span>
          <Select value={selectedModel} onValueChange={onModelChange}>
            <SelectTrigger className="w-56 h-9 border-gray-300">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {models.map((model) => (
                <SelectItem key={model.value} value={model.value}>
                  {model.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center space-x-1 border-l border-gray-200 pl-4">
          {onRefresh && (
            <Button variant="ghost" size="sm" onClick={onRefresh} className="h-8 w-8 p-0">
              <RefreshCw className="w-4 h-4 text-gray-600" />
            </Button>
          )}

          {onToggleDarkMode && (
            <Button variant="ghost" size="sm" onClick={onToggleDarkMode} className="h-8 w-8 p-0">
              <Moon className="w-4 h-4 text-gray-600" />
            </Button>
          )}

          {onSettings && (
            <Button variant="ghost" size="sm" onClick={onSettings} className="h-8 w-8 p-0">
              <Settings className="w-4 h-4 text-gray-600" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

