import { describe, it, expect, beforeEach } from 'vitest'
import { useConfigStore } from '../configStore'
import { Config } from '@/types/api'

describe('configStore', () => {
  beforeEach(() => {
    useConfigStore.setState({
      configs: [],
      selectedConfig: null,
      activeSection: 'addresses',
      loading: false,
      stats: {},
    })
  })

  it('sets configs', () => {
    const configs: Config[] = [
      { name: 'test1', path: '/test1', size: 1000, modified: '2024-01-01' },
      { name: 'test2', path: '/test2', size: 2000, modified: '2024-01-02' },
    ]
    
    useConfigStore.getState().setConfigs(configs)
    
    expect(useConfigStore.getState().configs).toEqual(configs)
  })

  it('sets selected config', () => {
    const config: Config = { name: 'test', path: '/test', size: 1000, modified: '2024-01-01' }
    
    useConfigStore.getState().setSelectedConfig(config)
    
    expect(useConfigStore.getState().selectedConfig).toEqual(config)
  })

  it('sets active section', () => {
    useConfigStore.getState().setActiveSection('services')
    
    expect(useConfigStore.getState().activeSection).toBe('services')
  })

  it('sets loading state', () => {
    useConfigStore.getState().setLoading(true)
    
    expect(useConfigStore.getState().loading).toBe(true)
  })

  it('sets all stats', () => {
    const stats = {
      addresses: 100,
      services: 50,
      'address-groups': 25,
    }
    
    useConfigStore.getState().setStats(stats)
    
    expect(useConfigStore.getState().stats).toEqual(stats)
  })

  it('updates individual stat', () => {
    useConfigStore.getState().setStats({ addresses: 100 })
    useConfigStore.getState().updateStat('services', 50)
    
    expect(useConfigStore.getState().stats).toEqual({
      addresses: 100,
      services: 50,
    })
  })
})