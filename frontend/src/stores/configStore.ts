import { create } from 'zustand'
import { Config } from '@/types/api'

interface ConfigStore {
  configs: Config[]
  selectedConfig: Config | null
  activeSection: string
  loading: boolean
  stats: Record<string, number>
  setConfigs: (configs: Config[]) => void
  setSelectedConfig: (config: Config | null) => void
  setActiveSection: (section: string) => void
  setLoading: (loading: boolean) => void
  setStats: (stats: Record<string, number>) => void
  updateStat: (key: string, value: number) => void
}

export const useConfigStore = create<ConfigStore>((set) => ({
  configs: [],
  selectedConfig: null,
  activeSection: 'addresses',
  loading: false,
  stats: {},
  setConfigs: (configs) => set({ configs }),
  setSelectedConfig: (config) => set({ selectedConfig: config }),
  setActiveSection: (section) => set({ activeSection: section }),
  setLoading: (loading) => set({ loading }),
  setStats: (stats) => set({ stats }),
  updateStat: (key, value) => set((state) => ({ 
    stats: { ...state.stats, [key]: value } 
  })),
}))