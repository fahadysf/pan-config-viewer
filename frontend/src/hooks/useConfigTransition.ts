import { useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useConfigStore } from '@/stores/configStore'

/**
 * Hook to manage config transitions and prevent browser hanging
 * Ensures smooth switching between configurations by properly
 * cleaning up queries and managing loading states
 */
export function useConfigTransition() {
  const queryClient = useQueryClient()
  const { selectedConfig, isTransitioning } = useConfigStore()
  const previousConfigRef = useRef(selectedConfig?.name)
  
  useEffect(() => {
    // Only run cleanup when config actually changes
    if (previousConfigRef.current !== selectedConfig?.name) {
      const cleanup = async () => {
        // Cancel all queries for the previous config
        await queryClient.cancelQueries({
          predicate: (query) => {
            const key = query.queryKey
            // Keep config list query, cancel everything else
            if (Array.isArray(key) && key[0] === 'configs') {
              return false
            }
            // Cancel queries that include the old config name
            if (Array.isArray(key) && key.includes(previousConfigRef.current)) {
              return true
            }
            return false
          }
        })
        
        // Remove stale queries from cache
        queryClient.removeQueries({
          predicate: (query) => {
            const key = query.queryKey
            if (Array.isArray(key) && key[0] === 'configs') {
              return false
            }
            // Remove queries for old config
            if (Array.isArray(key) && key.includes(previousConfigRef.current)) {
              return true
            }
            return false
          }
        })
      }
      
      cleanup()
      previousConfigRef.current = selectedConfig?.name
    }
  }, [selectedConfig?.name, queryClient])
  
  return { isTransitioning }
}