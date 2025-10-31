import React, { useState, useEffect } from 'react'
import { X, Save, Server } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'

interface MCPServerConfig {
  name: string
  command: string
  args: string[]
  env?: Record<string, string>
}

interface MCPConfigDialogProps {
  isOpen: boolean
  onClose: () => void
  onSave: (config: MCPServerConfig) => void
  existingConfig?: MCPServerConfig
}

export const MCPConfigDialog: React.FC<MCPConfigDialogProps> = ({
  isOpen,
  onClose,
  onSave,
  existingConfig,
}) => {
  const [name, setName] = useState('')
  const [command, setCommand] = useState('')
  const [args, setArgs] = useState('')
  const [envKeys, setEnvKeys] = useState<Array<{ key: string; value: string }>>([])

  useEffect(() => {
    if (isOpen) {
      if (existingConfig) {
        setName(existingConfig.name)
        setCommand(existingConfig.command)
        setArgs(existingConfig.args.join(' '))
        if (existingConfig.env) {
          setEnvKeys(
            Object.entries(existingConfig.env).map(([key, value]) => ({ key, value }))
          )
        } else {
          setEnvKeys([])
        }
      } else {
        // Reset form for new server
        setName('')
        setCommand('')
        setArgs('')
        setEnvKeys([])
      }
    }
  }, [isOpen, existingConfig])

  const handleSave = () => {
    if (!name.trim() || !command.trim()) {
      alert('Please fill in at least Name and Command fields')
      return
    }

    const config: MCPServerConfig = {
      name: name.trim(),
      command: command.trim(),
      args: args
        .split(' ')
        .map((arg) => arg.trim())
        .filter((arg) => arg.length > 0),
      env:
        envKeys.length > 0
          ? envKeys.reduce((acc, item) => {
              if (item.key.trim()) {
                acc[item.key.trim()] = item.value.trim()
              }
              return acc
            }, {} as Record<string, string>)
          : undefined,
    }

    onSave(config)
  }

  const addEnvVar = () => {
    setEnvKeys([...envKeys, { key: '', value: '' }])
  }

  const removeEnvVar = (index: number) => {
    setEnvKeys(envKeys.filter((_, i) => i !== index))
  }

  const updateEnvVar = (index: number, field: 'key' | 'value', value: string) => {
    const updated = [...envKeys]
    updated[index] = { ...updated[index], [field]: value }
    setEnvKeys(updated)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Server className="w-6 h-6 text-veeam" />
            <h2 className="text-2xl font-semibold text-gray-900">
              {existingConfig ? 'Edit MCP Server' : 'Add MCP Server'}
            </h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {/* Server Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Server Name <span className="text-red-500">*</span>
              </label>
              <Input
                type="text"
                placeholder="e.g., veeam-mcp-server"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">A unique identifier for this MCP server</p>
            </div>

            {/* Command */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Command <span className="text-red-500">*</span>
              </label>
              <Input
                type="text"
                placeholder="e.g., node, python, npx"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">The executable command to run the MCP server</p>
            </div>

            {/* Arguments */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Arguments
              </label>
              <Input
                type="text"
                placeholder="e.g., path/to/server.js --port 3000"
                value={args}
                onChange={(e) => setArgs(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                Space-separated arguments to pass to the command
              </p>
            </div>

            {/* Environment Variables */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Environment Variables
                </label>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={addEnvVar}
                  type="button"
                >
                  Add Variable
                </Button>
              </div>

              {envKeys.length === 0 ? (
                <p className="text-sm text-gray-500 italic">
                  No environment variables. Click "Add Variable" to add one.
                </p>
              ) : (
                <div className="space-y-2">
                  {envKeys.map((env, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <Input
                        type="text"
                        placeholder="Variable name"
                        value={env.key}
                        onChange={(e) => updateEnvVar(index, 'key', e.target.value)}
                        className="flex-1"
                      />
                      <Input
                        type="text"
                        placeholder="Value"
                        value={env.value}
                        onChange={(e) => updateEnvVar(index, 'value', e.target.value)}
                        className="flex-1"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeEnvVar(index)}
                        type="button"
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Preview */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Configuration Preview</h4>
              <pre className="text-xs text-gray-700 overflow-x-auto">
                {JSON.stringify(
                  {
                    [name || 'server-name']: {
                      command: command || 'command',
                      args: args
                        .split(' ')
                        .map((a) => a.trim())
                        .filter((a) => a),
                      ...(envKeys.length > 0 &&
                        envKeys.some((e) => e.key.trim()) && {
                          env: envKeys.reduce((acc, item) => {
                            if (item.key.trim()) {
                              acc[item.key.trim()] = item.value.trim()
                            }
                            return acc
                          }, {} as Record<string, string>),
                        }),
                    },
                  },
                  null,
                  2
                )}
              </pre>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 flex justify-end space-x-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            className="bg-veeam hover:bg-veeam-dark text-white"
            disabled={!name.trim() || !command.trim()}
          >
            <Save className="w-4 h-4 mr-2" />
            Save
          </Button>
        </div>
      </div>
    </div>
  )
}

