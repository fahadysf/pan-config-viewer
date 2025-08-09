import { create } from 'zustand'

interface LoadingState {
  statsLoading: boolean
  statsLoaded: boolean
  dataEnabled: boolean
  loadingProgress: number
  loadingMessage: string
  
  // Actions
  setStatsLoading: (loading: boolean) => void
  setStatsLoaded: (loaded: boolean) => void
  setDataEnabled: (enabled: boolean) => void
  setLoadingProgress: (progress: number) => void
  setLoadingMessage: (message: string) => void
  resetLoadingState: () => void
}

export const useLoadingStore = create<LoadingState>((set) => ({
  statsLoading: false,
  statsLoaded: false,
  dataEnabled: false,
  loadingProgress: 0,
  loadingMessage: '',
  
  setStatsLoading: (loading) => set({ statsLoading: loading }),
  setStatsLoaded: (loaded) => set({ statsLoaded: loaded }),
  setDataEnabled: (enabled) => set({ dataEnabled: enabled }),
  setLoadingProgress: (progress) => set({ loadingProgress: progress }),
  setLoadingMessage: (message) => set({ loadingMessage: message }),
  resetLoadingState: () => set({
    statsLoading: false,
    statsLoaded: false,
    dataEnabled: false,
    loadingProgress: 0,
    loadingMessage: ''
  }),
}))