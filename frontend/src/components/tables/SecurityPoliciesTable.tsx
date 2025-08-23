import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { configApi } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import { useDebouncedFilters } from '@/hooks/useDebouncedFilters'
import { SecurityPolicy, ColumnFilter } from '@/types/api'
import { 
  Eye, 
  MoreHorizontal, 
  Loader2, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Info
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { FilterableColumnHeader } from '@/components/ui/filterable-column-header'
import { DetailModal } from '@/components/modals/DetailModal'

// Memoized action badge component
const ActionBadge = React.memo(({ action }: { action: string }) => {
  const getActionColor = (action: string) => {
    switch (action.toLowerCase()) {
      case 'allow':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'deny':
      case 'drop':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'reset-client':
      case 'reset-server':
      case 'reset-both':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getActionIcon = (action: string) => {
    switch (action.toLowerCase()) {
      case 'allow':
        return <CheckCircle className="h-3 w-3" />
      case 'deny':
      case 'drop':
        return <XCircle className="h-3 w-3" />
      case 'reset-client':
      case 'reset-server':
      case 'reset-both':
        return <AlertTriangle className="h-3 w-3" />
      default:
        return <Info className="h-3 w-3" />
    }
  }

  return (
    <Badge 
      variant="outline" 
      className={`${getActionColor(action)} flex items-center gap-1`}
    >
      {getActionIcon(action)}
      {action}
    </Badge>
  )
})

ActionBadge.displayName = 'ActionBadge'

// Memoized zones cell component
const ZonesCell = React.memo(({ zones }: { zones: string[] }) => {
  if (!zones || zones.length === 0) {
    return <span className="text-gray-400 text-sm">any</span>
  }
  
  return (
    <div className="flex flex-wrap gap-1">
      {zones.map((zone, index) => (
        <Badge key={index} variant="secondary" className="text-xs">
          {zone}
        </Badge>
      ))}
    </div>
  )
})

ZonesCell.displayName = 'ZonesCell'

// Memoized list cell component for addresses, applications, services
const ListCell = React.memo(({ items }: { items: string[] }) => {
  if (!items || items.length === 0) {
    return <span className="text-gray-400 text-sm">any</span>
  }
  
  const displayItems = items.slice(0, 3)
  const remainingCount = items.length - 3
  
  return (
    <div className="space-y-1">
      {displayItems.map((item, index) => (
        <div key={index} className="text-sm">{item}</div>
      ))}
      {remainingCount > 0 && (
        <span className="text-xs text-gray-500">+{remainingCount} more</span>
      )}
    </div>
  )
})

ListCell.displayName = 'ListCell'

export function SecurityPoliciesTable() {
  const { selectedConfig, updateStat } = useConfigStore()
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
  const [detailItem, setDetailItem] = useState<SecurityPolicy | null>(null)
  const [isInitialLoad, setIsInitialLoad] = useState(true)
  const [displayData, setDisplayData] = useState<SecurityPolicy[]>([])
  const [isTransitioning, setIsTransitioning] = useState(false)
  
  // Use debounced filters
  const {
    filters,
    debouncedFilters,
    isDebouncing,
    handleFiltersChange: handleFiltersChangeDebounced,
    resetFilters
  } = useDebouncedFilters([], 300) // 300ms debounce

  // Handle filter changes with proper state updates
  const handleFiltersChange = useCallback((newFilters: ColumnFilter[]) => {
    // Reset pagination when filters change
    setPagination(prev => ({ ...prev, pageIndex: 0 }))
    // Update filters
    handleFiltersChangeDebounced(newFilters)
  }, [handleFiltersChangeDebounced])

  // Query for security policies
  const { data, isLoading, error, isFetching } = useQuery({
    queryKey: ['security-policies', selectedConfig?.name, pagination, debouncedFilters],
    queryFn: () => {
      if (!selectedConfig?.name) return null
      return configApi.getSecurityPolicies(
        selectedConfig.name,
        pagination.pageIndex + 1, // API uses 1-based pagination
        pagination.pageSize,
        debouncedFilters
      )
    },
    enabled: !!selectedConfig?.name,
    placeholderData: (previousData) => previousData,
    staleTime: 5 * 60 * 1000, // Consider data stale after 5 minutes
  })

  // Update display data
  useEffect(() => {
    if (data?.items && !isLoading) {
      setIsTransitioning(true)
      setDisplayData(data.items)
      setIsTransitioning(false)
      setIsInitialLoad(false)
    }
  }, [data?.items, isLoading])

  // Update stats when data changes
  useEffect(() => {
    if (data?.total_items !== undefined) {
      updateStat('security-policies', data.total_items)
    }
  }, [data?.total_items, updateStat])

  // Column definitions with proper memoization
  const columns = useMemo<ColumnDef<SecurityPolicy>[]>(() => [
    {
      accessorKey: 'order',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Order"
          field="order" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => (
        <span className="font-mono text-sm">{row.original.order || '-'}</span>
      ),
      size: 80,
    },
    {
      accessorKey: 'name',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Rule Name"
          field="name" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => (
        <span className="font-medium text-xs">{row.original.name}</span>
      ),
      size: 200,
    },
    {
      accessorKey: 'rule_type',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Type"
          field="rule_type" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => (
        <Badge variant="outline">{row.original.rule_type}</Badge>
      ),
      size: 100,
    },
    {
      accessorKey: 'from',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Source Zones"
          field="from" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => <ZonesCell zones={row.original.from} />,
      size: 150,
    },
    {
      accessorKey: 'source',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Source"
          field="source" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => <ListCell items={row.original.source} />,
      size: 200,
    },
    {
      accessorKey: 'to',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Dest Zones"
          field="to" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => <ZonesCell zones={row.original.to} />,
      size: 150,
    },
    {
      accessorKey: 'destination',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Destination"
          field="destination" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => <ListCell items={row.original.destination} />,
      size: 200,
    },
    {
      accessorKey: 'application',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Applications"
          field="application" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => <ListCell items={row.original.application} />,
      size: 150,
    },
    {
      accessorKey: 'service',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Services"
          field="service" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => <ListCell items={row.original.service} />,
      size: 150,
    },
    {
      accessorKey: 'action',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Action"
          field="action" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => <ActionBadge action={row.original.action} />,
      size: 100,
    },
    {
      accessorKey: 'log_setting',
      header: ({ column }) => (
        <FilterableColumnHeader 
          column={column} 
          title="Logging"
          field="log_setting" 
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => {
        const logSetting = row.original.log_setting
        if (!logSetting || logSetting === 'none') {
          return <span className="text-gray-400 text-sm">None</span>
        }
        return <Badge variant="secondary">{logSetting}</Badge>
      },
      size: 100,
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
      cell: ({ row }) => (
        <span className="text-sm text-gray-600">
          {row.original.description || '-'}
        </span>
      ),
      size: 200,
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => {
        const policy = row.original
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
              <DropdownMenuItem onClick={() => setDetailItem(policy)}>
                <Eye className="mr-2 h-4 w-4" />
                View details
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
      size: 50,
    },
  ], [filters, handleFiltersChange])

  // Show skeleton during initial load
  if (isInitialLoad && isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-600">
        <p>Error loading security policies: {(error as Error).message}</p>
      </div>
    )
  }

  // Calculate if we're showing filtered results
  const isFiltered = filters.length > 0
  const showingFilteredText = isFiltered ? 
    `Showing ${displayData.length} of ${data?.total_items || 0} policies (filtered)` :
    `Showing ${displayData.length} of ${data?.total_items || 0} policies`

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold tracking-tight">Security Policies</h2>
          <p className="text-muted-foreground">
            Manage firewall security rules and policies
          </p>
        </div>
        {filters.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              resetFilters()
              setPagination(prev => ({ ...prev, pageIndex: 0 }))
            }}
          >
            Clear filters ({filters.length})
          </Button>
        )}
      </div>

      <div className="text-sm text-gray-600 flex items-center gap-2">
        {showingFilteredText}
        {(isFetching || isDebouncing || isTransitioning) && (
          <Loader2 className="h-4 w-4 animate-spin" />
        )}
      </div>

      <DataTable
        columns={columns}
        data={displayData}
        pageCount={data?.total_pages}
        pagination={pagination}
        onPaginationChange={setPagination}
        loading={isFetching || isDebouncing || isTransitioning}
      />

      {detailItem && (
        <DetailModal
          item={detailItem}
          onClose={() => setDetailItem(null)}
        />
      )}
    </div>
  )
}