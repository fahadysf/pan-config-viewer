import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useConfigStore } from '@/stores/configStore'
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
  const { configs, selectedConfig, setConfigs, setSelectedConfig, setLoading } = useConfigStore()

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
          <h1 className="text-2xl font-bold text-gray-900">PAN-OS Configuration Viewer</h1>
          
          <Select
            value={selectedConfig?.name || ''}
            onValueChange={(value) => {
              const config = configs.find(c => c.name === value)
              setSelectedConfig(config || null)
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