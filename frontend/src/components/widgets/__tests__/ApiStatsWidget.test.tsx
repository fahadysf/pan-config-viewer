import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ApiStatsWidget } from '../ApiStatsWidget'
import { useApiStatsStore } from '@/stores/apiStatsStore'
import { ApiStats } from '@/types/api'

vi.mock('@/stores/apiStatsStore')

describe('ApiStatsWidget', () => {
  const mockToggleCollapsed = vi.fn()
  
  const mockStats: ApiStats[] = [
    {
      endpoint: '/api/v1/configs/test/addresses',
      query_time: 150,
      items_retrieved: 100,
      timestamp: Date.now(),
    },
    {
      endpoint: '/api/v1/configs/test/services',
      query_time: 75,
      items_retrieved: 50,
      timestamp: Date.now() - 5000,
    },
  ]

  beforeEach(() => {
    vi.mocked(useApiStatsStore).mockReturnValue({
      isCollapsed: false,
      toggleCollapsed: mockToggleCollapsed,
      stats: [],
      addStat: vi.fn(),
      clearStats: vi.fn(),
    })
  })

  it('renders nothing when no stats', () => {
    const { container } = render(<ApiStatsWidget stats={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders stats widget with data', () => {
    render(<ApiStatsWidget stats={mockStats} />)
    
    expect(screen.getByText('API Statistics')).toBeInTheDocument()
    expect(screen.getByText('/api/v1/configs/test/addresses')).toBeInTheDocument()
    expect(screen.getByText('150ms')).toBeInTheDocument()
    expect(screen.getByText('100 items')).toBeInTheDocument()
  })

  it('shows collapsed state', () => {
    vi.mocked(useApiStatsStore).mockReturnValue({
      isCollapsed: true,
      toggleCollapsed: mockToggleCollapsed,
      stats: [],
      addStat: vi.fn(),
      clearStats: vi.fn(),
    })
    
    render(<ApiStatsWidget stats={mockStats} />)
    
    // When collapsed, shows the latest query time in parentheses
    expect(screen.getByText('API Statistics')).toBeInTheDocument()
    // The query time is shown, check it's rendered within the collapsed view
    const container = screen.getByText('API Statistics').parentElement
    expect(container?.textContent).toContain('150ms')
    expect(screen.queryByText('100 items')).not.toBeInTheDocument()
  })

  it('toggles collapse state on click', () => {
    render(<ApiStatsWidget stats={mockStats} />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    expect(mockToggleCollapsed).toHaveBeenCalled()
  })

  it('shows only last 5 stats', () => {
    const manyStats = Array.from({ length: 10 }, (_, i) => ({
      endpoint: `/api/v1/endpoint${i}`,
      query_time: 100 + i,
      items_retrieved: 10 + i,
      timestamp: Date.now() - i * 1000,
    }))
    
    render(<ApiStatsWidget stats={manyStats} />)
    
    expect(screen.queryByText('/api/v1/endpoint0')).not.toBeInTheDocument()
    expect(screen.getByText('/api/v1/endpoint9')).toBeInTheDocument()
  })
})