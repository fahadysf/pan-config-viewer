import { create } from 'zustand'
import { ApiStats } from '@/types/api'

interface ApiStatsStore {
  stats: ApiStats[]
  isCollapsed: boolean
  addStat: (stat: ApiStats) => void
  clearStats: () => void
  toggleCollapsed: () => void
}

export const useApiStatsStore = create<ApiStatsStore>((set) => ({
  stats: [],
  isCollapsed: true,
  addStat: (stat) => set((state) => ({ 
    stats: [...state.stats.slice(-9), stat] // Keep last 10 stats
  })),
  clearStats: () => set({ stats: [] }),
  toggleCollapsed: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
}))