import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useConfigStore } from '@/stores/configStore'
import { useLoadingStore } from '@/stores/loadingStore'
import { configApi } from '@/services/api'

// Define the stats we need to fetch
const STAT_TYPES = [
  'addresses',
  'address-groups',
  'services',
  'service-groups',
  'device-groups',
  'security-rules',
  'templates'
] as const

export function useConfigStats() {
  const { selectedConfig, updateStat } = useConfigStore()
  const { 
    setStatsLoading, 
    setStatsLoaded, 
    setDataEnabled,
    setLoadingProgress,
    setLoadingMessage,
    resetLoadingState
  } = useLoadingStore()

  // Reset loading state when config changes
  useEffect(() => {
    console.log('useConfigStats: selectedConfig changed:', selectedConfig?.name)
    if (selectedConfig) {
      resetLoadingState()
      setStatsLoading(true)
      setLoadingMessage('Loading configuration statistics...')
    }
  }, [selectedConfig?.name, resetLoadingState, setStatsLoading, setLoadingMessage])

  // Fetch basic config info first
  const { data: configInfo } = useQuery({
    queryKey: ['config-info', selectedConfig?.name],
    queryFn: async () => {
      if (!selectedConfig) return null
      setLoadingProgress(10)
      const info = await configApi.getConfigInfo(selectedConfig.name)
      setLoadingProgress(20)
      return info
    },
    enabled: !!selectedConfig,
    staleTime: 5 * 60 * 1000,
  })

  // Fetch stats for each object type
  const statsQueries = STAT_TYPES.map((type, index) => {
    return useQuery({
      queryKey: ['stats', selectedConfig?.name, type],
      queryFn: async () => {
        if (!selectedConfig) return null
        
        try {
          // Use a lightweight endpoint that just returns counts
          const response = await fetch(
            `/api/v1/configs/${selectedConfig.name}/${type}?page=1&page_size=1`
          )
          const data = await response.json()
          
          // Update progress
          const progress = 20 + ((index + 1) / STAT_TYPES.length) * 70
          setLoadingProgress(progress)
          setLoadingMessage(`Loading ${type} statistics...`)
          
          // Update the stat in the store
          const statKey = type.replace('-', '_')
          updateStat(statKey, data.total_items || 0)
          
          return data.total_items || 0
        } catch (error) {
          console.error(`Error fetching stats for ${type}:`, error)
          return 0
        }
      },
      enabled: !!selectedConfig && !!configInfo,
      staleTime: 5 * 60 * 1000,
    })
  })

  // Check if all stats are loaded
  useEffect(() => {
    const allLoaded = statsQueries.every(query => !query.isLoading && query.data !== undefined)
    const anyLoading = statsQueries.some(query => query.isLoading)
    
    if (allLoaded && !anyLoading && selectedConfig) {
      setStatsLoaded(true)
      setStatsLoading(false)
      setLoadingProgress(100)
      setLoadingMessage('Statistics loaded')
      
      // Enable data fetching after a short delay to ensure UI updates
      setTimeout(() => {
        setDataEnabled(true)
      }, 100)
    }
  }, [statsQueries, selectedConfig, setStatsLoaded, setStatsLoading, setDataEnabled, setLoadingProgress, setLoadingMessage])

  return {
    isLoadingStats: statsQueries.some(query => query.isLoading),
    statsLoaded: statsQueries.every(query => !query.isLoading && query.data !== undefined),
  }
}