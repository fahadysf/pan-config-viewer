import { create } from 'zustand'
import { Config } from '@/types/api'

interface ConfigStore {
  configs: Config[]
  selectedConfig: Config | null
  activeSection: string
  loading: boolean
  stats: Record<string, number>
  isTransitioning: boolean
  setConfigs: (configs: Config[]) => void
  setSelectedConfig: (config: Config | null) => void
  setActiveSection: (section: string) => void
  setLoading: (loading: boolean) => void
  setStats: (stats: Record<string, number>) => void
  updateStat: (key: string, value: number) => void
  setTransitioning: (transitioning: boolean) => void
  resetStats: () => void
}

export const useConfigStore = create<ConfigStore>((set) => ({
  configs: [],
  selectedConfig: null,
  activeSection: 'addresses',
  loading: false,
  stats: {},
  isTransitioning: false,
  setConfigs: (configs) => set({ configs }),
  setSelectedConfig: (config) => set({ selectedConfig: config }),
  setActiveSection: (section) => set({ activeSection: section }),
  setLoading: (loading) => set({ loading }),
  setStats: (stats) => set({ stats }),
  updateStat: (key, value) => set((state) => ({ 
    stats: { ...state.stats, [key]: value } 
  })),
  setTransitioning: (transitioning) => set({ isTransitioning: transitioning }),
  resetStats: () => set({ stats: {} }),
}))