import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { configApi } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import { useDebouncedFilters } from '@/hooks/useDebouncedFilters'
import { Address, ColumnFilter } from '@/types/api'
import { Eye, MoreHorizontal, Loader2 } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { FilterableColumnHeader } from '@/components/ui/filterable-column-header'
import { DetailModal } from '@/components/modals/DetailModal'

// Memoized value cell component to prevent re-renders
const AddressValueCell = React.memo(({ address }: { address: Address }) => {
  let value = 'N/A'
  
  // Helper function to check if value is valid (not null, undefined, or empty string)
  const isValidValue = (val: string | null | undefined): boolean => {
    return val != null && val.trim() !== ''
  }
  
  // First, try to get value based on the type field
  switch (address.type) {
    case 'ip-netmask':
      if (isValidValue(address['ip-netmask'])) {
        value = address['ip-netmask']!
      }
      break
    case 'ip-range':
      if (isValidValue(address['ip-range'])) {
        value = address['ip-range']!
      }
      break
    case 'fqdn':
      if (isValidValue(address.fqdn)) {
        value = address.fqdn!
      }
      break
  }
  
  // If no value found for the specified type, try fallback to any available value
  if (value === 'N/A') {
    if (isValidValue(address['ip-netmask'])) {
      value = address['ip-netmask']!
    } else if (isValidValue(address['ip-range'])) {
      value = address['ip-range']!
    } else if (isValidValue(address.fqdn)) {
      value = address.fqdn!
    }
  }
  
  return (
    <code className={`text-sm px-2 py-1 rounded ${
      value === 'N/A' 
        ? 'bg-red-100 text-red-700' 
        : 'bg-gray-100 text-gray-800'
    }`}>
      {value}
    </code>
  )
})

AddressValueCell.displayName = 'AddressValueCell'

// Memoized location cell component
const AddressLocationCell = React.memo(({ address }: { address: Address }) => {
  const location = address['parent-device-group'] || 
                  address['parent-template'] || 
                  address['parent-vsys'] || 
                  'Shared'
  return <span className="text-sm">{location}</span>
})

AddressLocationCell.displayName = 'AddressLocationCell'

export function AddressesTable() {
  const { selectedConfig, updateStat } = useConfigStore()
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
  const [detailItem, setDetailItem] = useState<Address | null>(null)
  const [isInitialLoad, setIsInitialLoad] = useState(true)
  
  // Use debounced filters
  const {
    filters,
    debouncedFilters,
    isDebouncing,
    handleFiltersChange: handleFiltersChangeDebounced,
    resetFilters
  } = useDebouncedFilters([], 500) // 500ms debounce
  
  // Memoize handlers to prevent column recreation
  const handleFiltersChange = useCallback((newFilters: ColumnFilter[]) => {
    setPagination({ pageIndex: 0, pageSize: pagination.pageSize }) // Reset to first page
    handleFiltersChangeDebounced(newFilters)
  }, [pagination.pageSize, handleFiltersChangeDebounced])
  
  const handleDetailView = useCallback((item: Address) => {
    setDetailItem(item)
  }, [])

  // Reset pagination and filters when config changes
  useEffect(() => {
    setPagination({ pageIndex: 0, pageSize: 100 })
    resetFilters()
    setIsInitialLoad(true)
    setDetailItem(null)
  }, [selectedConfig?.name, resetFilters])

  const { data, isLoading, isFetching, error } = useQuery({
    queryKey: ['addresses', selectedConfig?.name, pagination, debouncedFilters],
    queryFn: async ({ signal }) => {
      if (!selectedConfig) return null
      
      try {
        const response = await configApi.getAddresses(
          selectedConfig.name,
          pagination.pageIndex + 1,
          pagination.pageSize,
          debouncedFilters
        )
        
        // Check if request was cancelled
        if (signal?.aborted) {
          return null
        }
        
        updateStat('addresses', response.total_items)
        setIsInitialLoad(false)
        return response
      } catch (error: any) {
        if (error?.name === 'CanceledError' || signal?.aborted) {
          return null
        }
        console.error('Error loading addresses:', error)
        throw error
      }
    },
    enabled: !!selectedConfig,
    staleTime: 30 * 1000,
    gcTime: 60 * 1000,
    refetchOnWindowFocus: false,
    retry: (failureCount, error: any) => {
      // Don't retry on cancellation
      if (error?.name === 'CanceledError') return false
      return failureCount < 1
    },
    retryDelay: 1000,
  })

  const columns: ColumnDef<Address>[] = useMemo(() => [
    {
      accessorKey: 'name',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Name"
          field="name"
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue('name')}</div>
      ),
    },
    {
      accessorKey: 'type',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Type"
          field="type"
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterOperators={[
            { value: 'eq', label: 'Equals', requiresValue: true, applicableTypes: ['text', 'number'] },
            { value: 'contains', label: 'Contains', requiresValue: true, applicableTypes: ['text'] },
          ]}
        />
      ),
      cell: ({ row }) => (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {row.getValue('type')}
        </span>
      ),
    },
    {
      accessorKey: 'value',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Value"
          field="ip-netmask,ip-range,fqdn"
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterOperators={[
            { value: 'contains', label: 'Contains', requiresValue: true, applicableTypes: ['text'] },
            { value: 'starts_with', label: 'Starts with', requiresValue: true, applicableTypes: ['text'] },
            { value: 'eq', label: 'Equals', requiresValue: true, applicableTypes: ['text', 'number'] },
            { value: 'regex', label: 'Regex', requiresValue: true, applicableTypes: ['text'] },
          ]}
        />
      ),
      cell: ({ row }) => <AddressValueCell address={row.original} />,
    },
    {
      accessorKey: 'location',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Location"
          field="parent-device-group,parent-template,parent-vsys"
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => <AddressLocationCell address={row.original} />,
    },
    {
      accessorKey: 'description',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Description"
          field="description"
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => {
        const description = row.getValue('description') as string
        return description ? (
          <span className="text-gray-600 text-sm">{description}</span>
        ) : (
          <span className="text-gray-400 text-sm italic">No description</span>
        )
      },
    },
    {
      id: 'actions',
      enableHiding: false,
      cell: ({ row }) => {
        const address = row.original

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => handleDetailView(address)}>
                <Eye className="mr-2 h-4 w-4" />
                View details
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ], [filters, handleFiltersChange, handleDetailView]) // Use memoized handlers

  // Show loading spinner when switching configs or initial load
  if (isLoading && isInitialLoad && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-900">
            Loading addresses...
          </p>
          <p className="text-xs text-gray-500 mt-1">This may take a moment for large configurations</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="text-center">
          <p className="text-sm font-medium text-red-600">Error loading addresses</p>
          <p className="text-xs text-gray-500 mt-1">{(error as Error).message}</p>
        </div>
      </div>
    )
  }


  return (
    <>
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Addresses</h2>
          <p className="text-muted-foreground">
            Manage network addresses and IP configurations
          </p>
        </div>
        
        <DataTable
          columns={columns}
          data={data?.items || []}
          pageCount={data?.total_pages}
          pagination={pagination}
          onPaginationChange={setPagination}
          loading={isFetching || isDebouncing}
        />
      </div>

      {detailItem && (
        <DetailModal
          item={detailItem}
          onClose={() => setDetailItem(null)}
        />
      )}
    </>
  )
}