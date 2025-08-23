import { useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useConfigStore } from '@/stores/configStore'
import { useLoadingStore } from '@/stores/loadingStore'
// import { useConfigStats } from '@/hooks/useConfigStats'
import { configApi } from '@/services/api'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function Header() {
  const { 
    configs, 
    selectedConfig, 
    setConfigs, 
    setSelectedConfig, 
    setLoading,
    setTransitioning,
    resetStats 
  } = useConfigStore()
  const { resetLoadingState } = useLoadingStore()
  const queryClient = useQueryClient()
  
  // Use the stats hook to trigger stats loading
  // const statsInfo = useConfigStats()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['configs'],
    queryFn: configApi.getConfigs,
  })

  useEffect(() => {
    if (data) {
      setConfigs(data)
      if (data.length > 0 && !selectedConfig) {
        setSelectedConfig(data[0])
      }
    }
  }, [data, selectedConfig, setConfigs, setSelectedConfig])

  useEffect(() => {
    setLoading(isLoading)
  }, [isLoading, setLoading])

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-bold text-gray-900">PAN-OS Configuration Viewer</h1>
          
          <Select
            value={selectedConfig?.name || ''}
            onValueChange={async (value) => {
              const config = configs.find(c => c.name === value)
              
              // Don't do anything if it's the same config
              if (config?.name === selectedConfig?.name) return
              
              // Start transition
              setTransitioning(true)
              resetStats()
              resetLoadingState()
              
              // Cancel current queries
              await queryClient.cancelQueries({
                predicate: (query) => query.queryKey[0] !== 'configs'
              })
              
              // Remove old queries from cache
              queryClient.removeQueries({
                predicate: (query) => {
                  const key = query.queryKey
                  // Keep configs query
                  if (Array.isArray(key) && key[0] === 'configs') return false
                  // Remove queries with old config name
                  if (Array.isArray(key) && key.includes(selectedConfig?.name)) return true
                  return false
                }
              })
              
              // Set the new config
              setSelectedConfig(config || null)
              
              // End transition quickly to allow queries to start
              setTimeout(() => {
                setTransitioning(false)
              }, 50)
            }}
          >
            <SelectTrigger className="w-[300px]">
              <SelectValue placeholder="Select a configuration" />
            </SelectTrigger>
            <SelectContent>
              {configs.map((config) => (
                <SelectItem key={config.name} value={config.name}>
                  {config.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="icon"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
          </Button>
        </div>

        {selectedConfig && (
          <div className="text-sm text-gray-500">
            <span>Size: {(selectedConfig.size / 1024 / 1024).toFixed(2)} MB</span>
            <span className="ml-4">Modified: {new Date(selectedConfig.modified).toLocaleDateString()}</span>
          </div>
        )}
      </div>
    </header>
  )
}