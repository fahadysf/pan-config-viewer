import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AddressesTable } from '../AddressesTable'
import { useConfigStore } from '@/stores/configStore'
import { configApi } from '@/services/api'

vi.mock('@/stores/configStore')
vi.mock('@/services/api')

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('AddressesTable', () => {
  const mockUpdateStat = vi.fn()
  
  beforeEach(() => {
    vi.mocked(useConfigStore).mockReturnValue({
      selectedConfig: { name: 'test-config', path: '/test', size: 1000, modified: '2024-01-01' },
      updateStat: mockUpdateStat,
      activeSection: 'addresses',
      configs: [],
      loading: false,
      stats: {},
      setConfigs: vi.fn(),
      setSelectedConfig: vi.fn(),
      setActiveSection: vi.fn(),
      setLoading: vi.fn(),
      setStats: vi.fn(),
    })
    
    vi.mocked(configApi.getAddresses).mockResolvedValue({
      items: [
        {
          xpath: '/config/shared/address/entry[1]',
          'parent-device-group': null,
          'parent-template': null,
          'parent-vsys': null,
          name: 'test-address',
          type: 'ip-netmask',
          'ip-netmask': '192.168.1.0/24',
          'ip-range': null,
          fqdn: null,
          description: 'Test network',
          tag: [],
        },
      ],
      total_items: 1,
      page: 1,
      page_size: 10,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    })
  })

  it('renders table with data', async () => {
    render(<AddressesTable />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('Addresses')).toBeInTheDocument()
      expect(screen.getByText('test-address')).toBeInTheDocument()
      expect(screen.getByText('192.168.1.0/24')).toBeInTheDocument()
      expect(screen.getByText('Test network')).toBeInTheDocument()
    })
  })

  it('displays type badges', async () => {
    render(<AddressesTable />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      const typeBadge = screen.getByText('ip-netmask')
      expect(typeBadge).toHaveClass('bg-blue-100')
    })
  })

  it('updates stats on data load', async () => {
    render(<AddressesTable />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(mockUpdateStat).toHaveBeenCalledWith('addresses', 1)
    })
  })

  it('shows loading state', () => {
    vi.mocked(configApi.getAddresses).mockImplementation(() => new Promise(() => {}))
    
    render(<AddressesTable />, { wrapper: createWrapper() })
    
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders empty state when no data', async () => {
    vi.mocked(configApi.getAddresses).mockResolvedValue({
      items: [],
      total_items: 0,
      page: 1,
      page_size: 10,
      total_pages: 0,
      has_next: false,
      has_previous: false,
    })
    
    render(<AddressesTable />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('No results.')).toBeInTheDocument()
    })
  })
})