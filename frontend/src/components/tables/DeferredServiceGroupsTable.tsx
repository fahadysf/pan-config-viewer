import { Suspense, lazy, useState, useEffect } from 'react'
import { useConfigStore } from '@/stores/configStore'
import { Loader2 } from 'lucide-react'

// Lazy load the actual table component
const ServiceGroupsTable = lazy(() => 
  import('./ServiceGroupsTable').then(module => ({
    default: module.ServiceGroupsTable
  }))
)

function LoadingFallback() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
      <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      <div className="text-center">
        <p className="text-sm font-medium text-gray-900">Loading service groups...</p>
        <p className="text-xs text-gray-500 mt-1">This may take a moment for large configurations</p>
      </div>
    </div>
  )
}

export function DeferredServiceGroupsTable() {
  const { selectedConfig } = useConfigStore()
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // Reset when config changes
    setIsReady(false)
    
    // Set ready after a brief delay to ensure cleanup
    if (selectedConfig) {
      const timer = setTimeout(() => {
        setIsReady(true)
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [selectedConfig?.name])

  if (!selectedConfig) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-gray-500">
        <div className="text-center">
          <p className="text-sm">No configuration selected</p>
        </div>
      </div>
    )
  }

  if (!isReady) {
    return <LoadingFallback />
  }

  // Keep the table mounted - let React Query handle loading states
  return (
    <Suspense fallback={<LoadingFallback />}>
      <ServiceGroupsTable />
    </Suspense>
  )
}