import React, { useState, useEffect } from 'react'
import { X, Save, Check, XCircle, AlertCircle, Plus, Edit2, Trash2 } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { chatAPI } from '@/services/api'
import { MCPConfigDialog } from './MCPConfigDialog'

interface ProviderStatus {
  provider: string
  configured: boolean
  healthy: boolean
  available_models: string[]
  error?: string
}

interface SettingsProps {
  isOpen: boolean
  onClose: () => void
}

export const Settings: React.FC<SettingsProps> = ({ isOpen, onClose }) => {
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({})
  const [providerStatuses, setProviderStatuses] = useState<ProviderStatus[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState<Record<string, boolean>>({})
  const [messages, setMessages] = useState<Record<string, string>>({})
  const [mcpServers, setMcpServers] = useState<Array<{ name: string; command: string; args: string[]; env?: Record<string, string> }>>([])
  const [showMCPDialog, setShowMCPDialog] = useState(false)
  const [editingMCP, setEditingMCP] = useState<any>(null)

  useEffect(() => {
    if (isOpen) {
      loadProviderStatuses()
      loadMCPServers()
    }
  }, [isOpen])

  const loadMCPServers = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/settings/mcp/servers')
      if (response.ok) {
        const servers = await response.json()
        setMcpServers(servers)
      }
    } catch (error) {
      console.error('Error loading MCP servers:', error)
    }
  }

  const handleSaveMCP = async (config: any) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/settings/mcp/servers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })

      if (response.ok) {
        await loadMCPServers()
        setShowMCPDialog(false)
        setEditingMCP(null)
        setMessages({ ...messages, mcp: 'MCP server saved successfully!' })
      } else {
        const data = await response.json()
        setMessages({ ...messages, mcp: data.detail || 'Failed to save MCP server' })
      }
    } catch (error) {
      setMessages({ ...messages, mcp: 'Error saving MCP server' })
    }
  }

  const handleDeleteMCP = async (serverName: string) => {
    if (!confirm(`Delete MCP server "${serverName}"?`)) return

    try {
      const response = await fetch(`http://localhost:8000/api/v1/settings/mcp/servers/${serverName}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        await loadMCPServers()
        setMessages({ ...messages, mcp: 'MCP server deleted' })
      }
    } catch (error) {
      console.error('Error deleting MCP server:', error)
    }
  }

  const loadProviderStatuses = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/settings/providers/status')
      const statuses: ProviderStatus[] = await response.json()
      setProviderStatuses(statuses)
    } catch (error) {
      console.error('Error loading provider statuses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveKey = async (provider: string) => {
    const apiKey = apiKeys[provider]
    if (!apiKey) {
      setMessages({ ...messages, [provider]: 'Please enter an API key' })
      return
    }

    setSaving({ ...saving, [provider]: true })
    setMessages({ ...messages, [provider]: '' })

    try {
      const response = await fetch('http://localhost:8000/api/v1/settings/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: apiKey }),
      })

      if (response.ok) {
        setMessages({ ...messages, [provider]: 'API key saved successfully!' })
        // Reload statuses to update health
        setTimeout(() => {
          loadProviderStatuses()
          setApiKeys({ ...apiKeys, [provider]: '' }) // Clear input
        }, 1000)
      } else {
        const data = await response.json()
        setMessages({ ...messages, [provider]: data.detail || 'Failed to save API key' })
      }
    } catch (error) {
      setMessages({ ...messages, [provider]: 'Error saving API key' })
    } finally {
      setSaving({ ...saving, [provider]: false })
    }
  }

  const handleDeleteKey = async (provider: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/settings/api-keys/${provider}`, {
        method: 'DELETE',
      })
      loadProviderStatuses()
      setMessages({ ...messages, [provider]: 'API key removed' })
    } catch (error) {
      console.error('Error deleting API key:', error)
    }
  }

  const getProviderName = (provider: string) => {
    const names: Record<string, string> = {
      openai: 'OpenAI',
      anthropic: 'Anthropic (Claude)',
      gemini: 'Google Gemini',
      ollama: 'Ollama (Local)',
    }
    return names[provider] || provider
  }

  const getStatusIcon = (status: ProviderStatus) => {
    if (!status.configured) {
      return <XCircle className="w-5 h-5 text-gray-400" />
    }
    if (status.healthy) {
      return <Check className="w-5 h-5 text-green-500" />
    }
    return <AlertCircle className="w-5 h-5 text-yellow-500" />
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-semibold text-gray-900">Settings</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-8">
            {/* API Keys Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">API Keys</h3>
              <p className="text-sm text-gray-600 mb-4">
                Configure API keys for each LLM provider. Keys are stored securely and only used for API calls.
              </p>

              {loading ? (
                <div className="text-center py-8">
                  <div className="text-gray-500">Loading provider statuses...</div>
                </div>
              ) : (
                <div className="space-y-4">
                  {providerStatuses.map((status) => (
                    <div
                      key={status.provider}
                      className="border border-gray-200 rounded-lg p-4 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(status)}
                          <div>
                            <div className="font-medium text-gray-900">
                              {getProviderName(status.provider)}
                            </div>
                            <div className="text-xs text-gray-500">
                              {status.configured
                                ? status.healthy
                                  ? 'Connected'
                                  : status.error || 'Connection failed'
                                : 'Not configured'}
                            </div>
                          </div>
                        </div>
                        {status.configured && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteKey(status.provider)}
                          >
                            Remove
                          </Button>
                        )}
                      </div>

                      {status.available_models.length > 0 && status.healthy && (
                        <div className="text-xs text-gray-500">
                          Available models: {status.available_models.slice(0, 3).join(', ')}
                          {status.available_models.length > 3 && '...'}
                        </div>
                      )}

                      {!status.configured && (
                        <div className="space-y-2">
                          <Input
                            type="password"
                            placeholder={`Enter ${getProviderName(status.provider)} API key`}
                            value={apiKeys[status.provider] || ''}
                            onChange={(e) =>
                              setApiKeys({ ...apiKeys, [status.provider]: e.target.value })
                            }
                            disabled={saving[status.provider]}
                          />
                          <div className="flex items-center justify-between">
                            <Button
                              onClick={() => handleSaveKey(status.provider)}
                              disabled={saving[status.provider] || !apiKeys[status.provider]}
                              className="bg-veeam hover:bg-veeam-dark text-white"
                              size="sm"
                            >
                              {saving[status.provider] ? (
                                <>Saving...</>
                              ) : (
                                <>
                                  <Save className="w-4 h-4 mr-2" />
                                  Save
                                </>
                              )}
                            </Button>
                            {messages[status.provider] && (
                              <span
                                className={`text-xs ${
                                  messages[status.provider].includes('success')
                                    ? 'text-green-600'
                                    : 'text-red-600'
                                }`}
                              >
                                {messages[status.provider]}
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {status.error && status.configured && (
                        <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                          Error: {status.error}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* MCP Configuration Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">MCP Servers</h3>
              <p className="text-sm text-gray-600 mb-4">
                Configure Model Context Protocol (MCP) servers to enable tool integration.
              </p>

              <div className="space-y-4">
                {/* Add New MCP Server */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-1">Add MCP Server</h4>
                      <p className="text-sm text-gray-500">
                        Configure Model Context Protocol servers to enable tool integration
                      </p>
                    </div>
                    <Button
                      className="bg-veeam hover:bg-veeam-dark text-white"
                      onClick={() => {
                        setEditingMCP(null)
                        setShowMCPDialog(true)
                      }}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Server
                    </Button>
                  </div>
                </div>

                {/* Existing MCP Servers */}
                {mcpServers.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="text-sm font-semibold text-gray-700">Configured Servers</h4>
                    {mcpServers.map((server) => (
                      <div
                        key={server.name}
                        className="border border-gray-200 rounded-lg p-4 bg-white"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <h5 className="font-medium text-gray-900">{server.name}</h5>
                            </div>
                            <div className="text-sm text-gray-600 space-y-1">
                              <div>
                                <span className="font-medium">Command:</span>{' '}
                                <code className="bg-gray-100 px-1 rounded">{server.command}</code>
                              </div>
                              {server.args.length > 0 && (
                                <div>
                                  <span className="font-medium">Args:</span>{' '}
                                  <code className="bg-gray-100 px-1 rounded">
                                    {server.args.join(' ')}
                                  </code>
                                </div>
                              )}
                              {server.env && Object.keys(server.env).length > 0 && (
                                <div>
                                  <span className="font-medium">Environment:</span>
                                  <pre className="text-xs bg-gray-100 p-2 rounded mt-1">
                                    {JSON.stringify(server.env, null, 2)}
                                  </pre>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2 ml-4">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setEditingMCP(server)
                                setShowMCPDialog(true)
                              }}
                            >
                              <Edit2 className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteMCP(server.name)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {messages.mcp && (
                  <div
                    className={`text-xs p-2 rounded ${
                      messages.mcp.includes('success')
                        ? 'bg-green-50 text-green-700'
                        : 'bg-red-50 text-red-700'
                    }`}
                  >
                    {messages.mcp}
                  </div>
                )}

                <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
                  <strong>Note:</strong> MCP server configuration will be saved to your config file.
                  You can edit the <code className="bg-white px-1 rounded">config/config.yaml</code> file directly
                  or use this interface.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 flex justify-end">
          <Button onClick={onClose} variant="outline">
            Close
          </Button>
        </div>
      </div>

      {/* MCP Config Dialog */}
      <MCPConfigDialog
        isOpen={showMCPDialog}
        onClose={() => {
          setShowMCPDialog(false)
          setEditingMCP(null)
        }}
        onSave={handleSaveMCP}
        existingConfig={editingMCP}
      />
    </div>
  )
}

