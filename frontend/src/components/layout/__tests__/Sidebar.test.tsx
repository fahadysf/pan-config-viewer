import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Sidebar } from '../Sidebar'
import { useConfigStore } from '@/stores/configStore'

vi.mock('@/stores/configStore')

describe('Sidebar', () => {
  const mockSetActiveSection = vi.fn()
  
  beforeEach(() => {
    vi.mocked(useConfigStore).mockReturnValue({
      activeSection: 'addresses',
      setActiveSection: mockSetActiveSection,
      stats: {
        addresses: 100,
        'address-groups': 50,
        services: 75,
      },
      configs: [],
      selectedConfig: null,
      loading: false,
      setConfigs: vi.fn(),
      setSelectedConfig: vi.fn(),
      setLoading: vi.fn(),
      setStats: vi.fn(),
      updateStat: vi.fn(),
    })
  })

  it('renders navigation items', () => {
    render(<Sidebar isOpen={true} onToggle={() => {}} />)
    
    expect(screen.getByText('Addresses')).toBeInTheDocument()
    expect(screen.getByText('Address Groups')).toBeInTheDocument()
    expect(screen.getByText('Services')).toBeInTheDocument()
    expect(screen.getByText('Service Groups')).toBeInTheDocument()
  })

  it('displays stats badges when open', () => {
    render(<Sidebar isOpen={true} onToggle={() => {}} />)
    
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
    expect(screen.getByText('75')).toBeInTheDocument()
  })

  it('hides text when collapsed', () => {
    render(<Sidebar isOpen={false} onToggle={() => {}} />)
    
    // When collapsed, Navigation heading is hidden with the "hidden" class
    const navigationHeading = screen.getByText('Navigation')
    expect(navigationHeading).toHaveClass('hidden')
    
    // Stats badges are not rendered when collapsed
    expect(screen.queryByText('100')).not.toBeInTheDocument()
  })

  it('calls setActiveSection when menu item is clicked', () => {
    render(<Sidebar isOpen={true} onToggle={() => {}} />)
    
    fireEvent.click(screen.getByText('Services'))
    expect(mockSetActiveSection).toHaveBeenCalledWith('services')
  })

  it('highlights active section', () => {
    render(<Sidebar isOpen={true} onToggle={() => {}} />)
    
    const addressButton = screen.getByText('Addresses').closest('button')
    expect(addressButton).toHaveClass('bg-blue-600')
  })

  it('toggles security profiles submenu', () => {
    render(<Sidebar isOpen={true} onToggle={() => {}} />)
    
    expect(screen.queryByText('Vulnerability Profiles')).not.toBeInTheDocument()
    
    fireEvent.click(screen.getByText('Security Profiles'))
    expect(screen.getByText('Vulnerability Profiles')).toBeInTheDocument()
    expect(screen.getByText('URL Filtering Profiles')).toBeInTheDocument()
  })
})