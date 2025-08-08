import { describe, it, expect, beforeEach } from 'vitest'
import { useApiStatsStore } from '../apiStatsStore'
import { ApiStats } from '@/types/api'

describe('apiStatsStore', () => {
  beforeEach(() => {
    useApiStatsStore.setState({
      stats: [],
      isCollapsed: true,
    })
  })

  it('adds stat to store', () => {
    const stat: ApiStats = {
      endpoint: '/api/test',
      query_time: 100,
      items_retrieved: 50,
      timestamp: Date.now(),
    }
    
    useApiStatsStore.getState().addStat(stat)
    
    expect(useApiStatsStore.getState().stats).toContain(stat)
  })

  it('keeps only last 10 stats', () => {
    const stats = Array.from({ length: 15 }, (_, i) => ({
      endpoint: `/api/test${i}`,
      query_time: 100 + i,
      items_retrieved: 10 + i,
      timestamp: Date.now() + i,
    }))
    
    stats.forEach(stat => useApiStatsStore.getState().addStat(stat))
    
    const storedStats = useApiStatsStore.getState().stats
    expect(storedStats).toHaveLength(10)
    expect(storedStats[0].endpoint).toBe('/api/test5')
    expect(storedStats[9].endpoint).toBe('/api/test14')
  })

  it('clears all stats', () => {
    const stat: ApiStats = {
      endpoint: '/api/test',
      query_time: 100,
      items_retrieved: 50,
      timestamp: Date.now(),
    }
    
    useApiStatsStore.getState().addStat(stat)
    useApiStatsStore.getState().clearStats()
    
    expect(useApiStatsStore.getState().stats).toHaveLength(0)
  })

  it('toggles collapsed state', () => {
    expect(useApiStatsStore.getState().isCollapsed).toBe(true)
    
    useApiStatsStore.getState().toggleCollapsed()
    expect(useApiStatsStore.getState().isCollapsed).toBe(false)
    
    useApiStatsStore.getState().toggleCollapsed()
    expect(useApiStatsStore.getState().isCollapsed).toBe(true)
  })
})