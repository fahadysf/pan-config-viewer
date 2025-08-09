import React from 'react'
import { useLoadingStore } from '@/stores/loadingStore'
import { useConfigStore } from '@/stores/configStore'
import { Loader2 } from 'lucide-react'

interface StatsLoadingWrapperProps {
  children: React.ReactNode
}

export function StatsLoadingWrapper({ children }: StatsLoadingWrapperProps) {
  const { selectedConfig } = useConfigStore()
  const { statsLoading, dataEnabled, loadingMessage, loadingProgress } = useLoadingStore()
  
  // Show loading spinner when stats are loading
  if (statsLoading || (!dataEnabled && selectedConfig)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-900">{loadingMessage || 'Initializing configuration...'}</p>
          {loadingProgress > 0 && (
            <div className="mt-4 w-64 mx-auto">
              <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${loadingProgress}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">{Math.round(loadingProgress)}% complete</p>
            </div>
          )}
          <p className="text-xs text-gray-400 mt-4">
            Loading configuration statistics to ensure smooth performance...
          </p>
        </div>
      </div>
    )
  }
  
  return <>{children}</>
}