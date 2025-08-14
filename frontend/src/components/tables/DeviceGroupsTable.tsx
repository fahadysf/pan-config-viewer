import { useState, useEffect, useCallback, useTransition } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { configApi } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import { DeviceGroup, ColumnFilter } from '@/types/api'
import { Eye, MoreHorizontal } from 'lucide-react'
import { useDebouncedFilters } from '@/hooks/useDebouncedFilters'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { FilterableColumnHeader } from '@/components/ui/filterable-column-header'
import { DetailModal } from '@/components/modals/DetailModal'

export function DeviceGroupsTable() {
  const { selectedConfig, updateStat } = useConfigStore()
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
  const [filters, setFilters] = useState<ColumnFilter[]>([])
  const [detailItem, setDetailItem] = useState<DeviceGroup | null>(null)
  const [displayData, setDisplayData] = useState<DeviceGroup[]>([])
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [, startTransition] = useTransition()
  
  const { debouncedFilters, handleFiltersChange: handleFiltersChangeBase } = useDebouncedFilters(filters)

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['device-groups', selectedConfig?.name, pagination, debouncedFilters],
    queryFn: async () => {
      if (!selectedConfig) return null
      const response = await configApi.getDeviceGroups(
        selectedConfig.name,
        pagination.pageIndex + 1,
        pagination.pageSize,
        debouncedFilters
      )
      updateStat('device-groups', response.total_items)
      return response
    },
    enabled: !!selectedConfig,
  })

  // Update display data when query data changes
  useEffect(() => {
    if (data?.items) {
      startTransition(() => {
        setDisplayData(data.items)
        setIsTransitioning(false)
      })
    }
  }, [data])

  // Handle filter changes with immediate UI feedback
  const handleFiltersChange = useCallback((newFilters: ColumnFilter[]) => {
    setIsTransitioning(true)
    // Don't clear data immediately - let the loading state show over existing data
    setPagination({ pageIndex: 0, pageSize: pagination.pageSize })
    setFilters(newFilters)
    handleFiltersChangeBase(newFilters)
  }, [pagination.pageSize, handleFiltersChangeBase])

  const columns: ColumnDef<DeviceGroup>[] = [
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
      accessorKey: 'parent-dg',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Parent DG"
          field="parent_dg"
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => {
        const group = row.original
        const parentDg = group['parent-dg']
        return parentDg ? (
          <span className="text-sm font-medium text-blue-600">{parentDg}</span>
        ) : (
          <span className="text-gray-400 text-sm italic">Root</span>
        )
      },
    },
    {
      accessorKey: 'devices_count',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Devices"
          field="devices_count"
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterOperators={[
            { value: 'gte', label: 'Count >= ', requiresValue: true, applicableTypes: ['number'] },
            { value: 'lte', label: 'Count <= ', requiresValue: true, applicableTypes: ['number'] },
            { value: 'eq', label: 'Count = ', requiresValue: true, applicableTypes: ['number'] },
          ]}
        />
      ),
      cell: ({ row }) => (
        <div className="text-center">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {row.getValue('devices_count')}
          </span>
        </div>
      ),
    },
    {
      accessorKey: 'objects',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Objects"
          field="address_count"
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterOperators={[
            { value: 'gte', label: 'Address Count >= ', requiresValue: true, applicableTypes: ['number'] },
            { value: 'lte', label: 'Address Count <= ', requiresValue: true, applicableTypes: ['number'] },
            { value: 'eq', label: 'Address Count = ', requiresValue: true, applicableTypes: ['number'] },
          ]}
        />
      ),
      cell: ({ row }) => {
        const group = row.original
        const addressCount = group.address_count + group['address-group-count']
        const serviceCount = group.service_count + group['service-group-count']
        return (
          <div className="text-sm space-y-1">
            <div>
              <span className="font-medium">Addresses:</span> {addressCount}
            </div>
            <div>
              <span className="font-medium">Services:</span> {serviceCount}
            </div>
          </div>
        )
      },
    },
    {
      accessorKey: 'policies',
      header: 'Security Policies',
      cell: ({ row }) => {
        const group = row.original
        const preRules = group['pre-security-rules-count']
        const postRules = group['post-security-rules-count']
        const totalRules = preRules + postRules
        return (
          <div className="text-sm space-y-1">
            <div>
              <span className="font-medium">Pre:</span> {preRules}
            </div>
            <div>
              <span className="font-medium">Post:</span> {postRules}
            </div>
            <div className="text-xs text-gray-500">Total: {totalRules}</div>
          </div>
        )
      },
    },
    {
      accessorKey: 'nat_policies',
      header: 'NAT Policies',
      cell: ({ row }) => {
        const group = row.original
        const preNat = group['pre-nat-rules-count']
        const postNat = group['post-nat-rules-count']
        const totalNat = preNat + postNat
        return (
          <div className="text-sm space-y-1">
            <div>
              <span className="font-medium">Pre:</span> {preNat}
            </div>
            <div>
              <span className="font-medium">Post:</span> {postNat}
            </div>
            <div className="text-xs text-gray-500">Total: {totalNat}</div>
          </div>
        )
      },
    },
    {
      accessorKey: 'location',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Location"
          field="xpath"
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
      ),
      cell: ({ row }) => {
        const group = row.original
        const location = group['parent-device-group'] || 
                        group['parent-template'] || 
                        group['parent-vsys'] || 
                        'Shared'
        return <span className="text-sm">{location}</span>
      },
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
        const group = row.original

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
              <DropdownMenuItem onClick={() => setDetailItem(group)}>
                <Eye className="mr-2 h-4 w-4" />
                View details
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <>
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Device Groups</h2>
          <p className="text-muted-foreground">
            Manage device group configurations and policies
          </p>
        </div>
        
        <DataTable
          columns={columns}
          data={displayData}
          pageCount={data?.total_pages}
          pagination={pagination}
          onPaginationChange={(newPagination) => {
            setIsTransitioning(true)
            setPagination(newPagination)
          }}
          loading={isLoading || isTransitioning || isFetching}
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