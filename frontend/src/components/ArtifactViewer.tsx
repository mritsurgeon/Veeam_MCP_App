import React from 'react'
import { X, Maximize2, Download } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/Tabs'
import { Button } from './ui/Button'
import { Artifact } from '@/types'

interface ArtifactViewerProps {
  artifact: Artifact | null
  onClose: () => void
  onExport?: (artifactId: string) => void
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifact,
  onClose,
  onExport,
}) => {
  if (!artifact) return null

  return (
    <div className="w-96 h-full border-l border-gray-200 bg-white flex flex-col">
      {/* Header */}
      <div className="h-12 border-b border-gray-200 flex items-center justify-between px-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 truncate">{artifact.title}</h3>
          <p className="text-xs text-gray-500">Click to open component</p>
        </div>
        <div className="flex items-center space-x-2">
          {onExport && (
            <Button variant="ghost" size="sm" onClick={() => onExport(artifact.id)}>
              <Download className="w-4 h-4" />
            </Button>
          )}
          <Button variant="ghost" size="sm">
            <Maximize2 className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="preview" className="flex-1 flex flex-col overflow-hidden">
        <div className="border-b border-gray-200 px-4">
          <TabsList className="bg-transparent">
            <TabsTrigger value="preview">Preview</TabsTrigger>
            <TabsTrigger value="code">Code</TabsTrigger>
          </TabsList>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          <TabsContent value="preview" className="mt-0">
            <div className="prose prose-sm max-w-none">
              {artifact.type === 'dashboard' && (
                <div>
                  <h2 className="text-lg font-semibold mb-2">{artifact.title}</h2>
                  <p className="text-sm text-gray-600 mb-4">
                    Real-time monitoring and analytics for your backup infrastructure
                  </p>
                  {/* Dashboard preview content would go here */}
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <h3 className="text-sm font-semibold mb-2">Backup Success Rate (Last 7 Days)</h3>
                    {/* Chart placeholder */}
                    <div className="h-48 bg-white rounded border border-gray-200 flex items-center justify-center text-gray-400 text-sm">
                      Chart visualization
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-semibold mb-2">Repository Storage Usage</h3>
                    {/* Storage chart placeholder */}
                    <div className="h-32 bg-white rounded border border-gray-200 flex items-center justify-center text-gray-400 text-sm">
                      Storage chart
                    </div>
                  </div>
                </div>
              )}

              {artifact.type === 'report' && (
                <div>
                  <h2 className="text-lg font-semibold mb-2">{artifact.title}</h2>
                  <p className="text-sm text-gray-500 mb-4">
                    Generated on {new Date().toLocaleDateString()}
                  </p>
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-semibold mb-2">Executive Summary</h3>
                      <div className="bg-gray-50 rounded-lg p-4">
                        {artifact.preview || artifact.content}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {artifact.type !== 'dashboard' && artifact.type !== 'report' && (
                <div className="whitespace-pre-wrap">{artifact.content}</div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="code" className="mt-0">
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
              <code>{artifact.code || artifact.content}</code>
            </pre>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  )
}

