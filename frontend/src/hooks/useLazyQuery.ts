import { useState, useEffect, useCallback } from 'react'
import { useQuery, UseQueryOptions } from '@tanstack/react-query'
import { lazyLoadingService } from '@/services/lazyApi'

interface LazyQueryOptions<T> extends Omit<UseQueryOptions<T>, 'queryFn'> {
  endpoint: string
  params?: Record<string, any>
  useLazyLoading?: boolean
  onProgress?: (progress: number) => void
  fallbackFn?: () => Promise<T>
}

interface LazyQueryResult<T> {
  data: T | undefined
  isLoading: boolean
  isLazyLoading: boolean
  error: any
  progress: number
  refetch: () => void
}

export function useLazyQuery<T>(options: LazyQueryOptions<T>): LazyQueryResult<T> {
  const [progress, setProgress] = useState(0)
  const [isLazyLoading, setIsLazyLoading] = useState(false)
  const [lazyLoadingAvailable, setLazyLoadingAvailable] = useState<boolean | null>(null)

  const {
    endpoint,
    params = {},
    useLazyLoading = true,
    onProgress,
    fallbackFn,
    ...queryOptions
  } = options

  // Check if lazy loading is available
  useEffect(() => {
    if (useLazyLoading) {
      lazyLoadingService.isLazyLoadingAvailable(endpoint).then(setLazyLoadingAvailable)
    } else {
      setLazyLoadingAvailable(false)
    }
  }, [endpoint, useLazyLoading])

  const handleProgress = useCallback((value: number) => {
    setProgress(value)
    if (onProgress) {
      onProgress(value)
    }
  }, [onProgress])

  const queryFn = useCallback(async () => {
    setProgress(0)
    
    // Use lazy loading if available and enabled
    if (useLazyLoading && lazyLoadingAvailable) {
      setIsLazyLoading(true)
      try {
        const result = await lazyLoadingService.fetchWithLazyLoading<T>(
          endpoint,
          params,
          handleProgress
        )
        return result
      } finally {
        setIsLazyLoading(false)
      }
    }
    
    // Otherwise use fallback function
    if (fallbackFn) {
      return await fallbackFn()
    }
    
    throw new Error('No query function available')
  }, [endpoint, params, useLazyLoading, lazyLoadingAvailable, fallbackFn, handleProgress])

  const query = useQuery<T>({
    ...queryOptions,
    queryFn,
    enabled: queryOptions.enabled !== false && lazyLoadingAvailable !== null,
  })

  return {
    data: query.data,
    isLoading: query.isLoading || isLazyLoading,
    isLazyLoading,
    error: query.error,
    progress,
    refetch: query.refetch,
  }
}