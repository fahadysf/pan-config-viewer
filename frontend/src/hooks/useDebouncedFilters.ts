import { useState, useEffect, useCallback, useRef } from 'react'
import { ColumnFilter } from '@/types/api'

/**
 * Hook to debounce filter changes and provide loading state
 * This prevents too many API calls when users are rapidly changing filters
 */
export function useDebouncedFilters(
  initialFilters: ColumnFilter[] = [],
  delay: number = 300
) {
  const [filters, setFilters] = useState<ColumnFilter[]>(initialFilters)
  const [debouncedFilters, setDebouncedFilters] = useState<ColumnFilter[]>(initialFilters)
  const [isDebouncing, setIsDebouncing] = useState(false)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Handle filter changes with debouncing
  const handleFiltersChange = useCallback((newFilters: ColumnFilter[]) => {
    setFilters(newFilters)
    setIsDebouncing(true)

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      setDebouncedFilters(newFilters)
      setIsDebouncing(false)
    }, delay)
  }, [delay])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  // Reset filters
  const resetFilters = useCallback(() => {
    setFilters([])
    setDebouncedFilters([])
    setIsDebouncing(false)
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
  }, [])

  return {
    filters,
    debouncedFilters,
    isDebouncing,
    handleFiltersChange,
    resetFilters,
  }
}