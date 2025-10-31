import React, { useState, useEffect } from 'react'
import { Wrench, Server, CheckCircle, XCircle, Loader } from 'lucide-react'
import { Button } from './ui/Button'

interface MCPTool {
  name: string
  description: string
  server: string
  enabled: boolean
}

interface MCPServer {
  name: string
  status: 'connected' | 'disconnected' | 'error'
  tools: MCPTool[]
  command?: string
  args?: string[]
}

export const ToolsPage: React.FC = () => {
  const [servers, setServers] = useState<MCPServer[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load MCP servers from backend
    loadMCPServers()
  }, [])

  const loadMCPServers = async () => {
    setLoading(true)
    try {
      // TODO: Replace with actual API endpoint when MCP integration is ready
      // const response = await fetch('http://localhost:8000/api/v1/mcp/servers')
      // const data = await response.json()
      
      // Mock data for now
      const mockServers: MCPServer[] = [
        {
          name: 'veeam-mcp-server',
          status: 'disconnected',
          tools: [
            {
              name: 'get_backup_jobs',
              description: 'Get list of Veeam backup jobs',
              server: 'veeam-mcp-server',
              enabled: false,
            },
            {
              name: 'get_repository_status',
              description: 'Get repository storage status',
              server: 'veeam-mcp-server',
              enabled: false,
            },
          ],
          command: 'node',
          args: ['path/to/veeam-mcp-server'],
        },
        {
          name: 'wazuh-mcp',
          status: 'disconnected',
          tools: [
            {
              name: 'search_alerts',
              description: 'Search Wazuh security alerts',
              server: 'wazuh-mcp',
              enabled: false,
            },
          ],
          command: 'python',
          args: ['path/to/wazuh-mcp'],
        },
      ]
      
      setServers(mockServers)
    } catch (error) {
      console.error('Error loading MCP servers:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <XCircle className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'connected':
        return 'Connected'
      case 'error':
        return 'Error'
      default:
        return 'Not Connected'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">MCP Tools</h1>
          <p className="text-gray-600">
            Manage and view available tools from connected MCP servers
          </p>
        </div>

        {servers.length === 0 ? (
          <div className="text-center py-12">
            <Wrench className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No MCP Servers Configured</h3>
            <p className="text-gray-500 mb-4">
              Configure MCP servers in Settings to see available tools here.
            </p>
            <Button className="bg-veeam hover:bg-veeam-dark text-white">
              Open Settings
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {servers.map((server) => (
              <div
                key={server.name}
                className="border border-gray-200 rounded-lg p-4 bg-white"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Server className="w-5 h-5 text-gray-400" />
                    <div>
                      <h3 className="font-semibold text-gray-900">{server.name}</h3>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        {getStatusIcon(server.status)}
                        <span>{getStatusText(server.status)}</span>
                      </div>
                    </div>
                  </div>
                  {server.status !== 'connected' && (
                    <Button variant="outline" size="sm">
                      Connect
                    </Button>
                  )}
                </div>

                {server.tools.length > 0 ? (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Available Tools:</h4>
                    {server.tools.map((tool) => (
                      <div
                        key={tool.name}
                        className="flex items-start justify-between p-3 bg-gray-50 rounded-md"
                      >
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <Wrench className="w-4 h-4 text-gray-400" />
                            <span className="font-mono text-sm font-medium text-gray-900">
                              {tool.name}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1 ml-6">{tool.description}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={tool.enabled}
                              onChange={() => {
                                // Toggle tool enabled state
                                setServers(
                                  servers.map((s) =>
                                    s.name === server.name
                                      ? {
                                          ...s,
                                          tools: s.tools.map((t) =>
                                            t.name === tool.name
                                              ? { ...t, enabled: !t.enabled }
                                              : t
                                          ),
                                        }
                                      : s
                                  )
                                )
                              }}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-veeam rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-veeam"></div>
                          </label>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No tools available from this server</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

