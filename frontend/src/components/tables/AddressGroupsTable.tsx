import { useState, useEffect, useCallback, useTransition } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { configApi } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import { AddressGroup, ColumnFilter } from '@/types/api'
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

export function AddressGroupsTable() {
  const { selectedConfig, updateStat } = useConfigStore()
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
  const [filters, setFilters] = useState<ColumnFilter[]>([])
  const [detailItem, setDetailItem] = useState<AddressGroup | null>(null)
  const [displayData, setDisplayData] = useState<AddressGroup[]>([])
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [, startTransition] = useTransition()
  
  const { debouncedFilters, handleFiltersChange: handleFiltersChangeBase } = useDebouncedFilters(filters)

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['address-groups', selectedConfig?.name, pagination, debouncedFilters],
    queryFn: async () => {
      if (!selectedConfig) return null
      const response = await configApi.getAddressGroups(
        selectedConfig.name,
        pagination.pageIndex + 1,
        pagination.pageSize,
        debouncedFilters
      )
      updateStat('address-groups', response.total_items)
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
    setDisplayData([]) // Immediately clear data
    setPagination({ pageIndex: 0, pageSize: pagination.pageSize })
    setFilters(newFilters)
    handleFiltersChangeBase(newFilters)
  }, [pagination.pageSize, handleFiltersChangeBase])

  const columns: ColumnDef<AddressGroup>[] = [
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
        <div className="font-medium text-xs">{row.getValue('name')}</div>
      ),
    },
    {
      accessorKey: 'type',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Type"
          field="static,dynamic"
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterOperators={[
            { value: 'eq', label: 'Equals', requiresValue: true, applicableTypes: ['text', 'number'] },
            { value: 'contains', label: 'Contains', requiresValue: true, applicableTypes: ['text'] },
          ]}
        />
      ),
      cell: ({ row }) => {
        const group = row.original
        const hasStaticMembers = group.static && group.static.length > 0
        const hasDynamicFilter = group.dynamic != null
        
        let type = 'Empty'
        let colorClass = 'bg-gray-100 text-gray-800'
        
        if (hasStaticMembers && hasDynamicFilter) {
          type = 'Mixed'
          colorClass = 'bg-purple-100 text-purple-800'
        } else if (hasStaticMembers) {
          type = 'Static'
          colorClass = 'bg-green-100 text-green-800'
        } else if (hasDynamicFilter) {
          type = 'Dynamic'
          colorClass = 'bg-blue-100 text-blue-800'
        }
        
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
            {type}
          </span>
        )
      },
    },
    {
      accessorKey: 'members',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Members/Filter"
          field="static"
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterOperators={[
            { value: 'contains', label: 'Contains', requiresValue: true, applicableTypes: ['text'] },
            { value: 'eq', label: 'Equals', requiresValue: true, applicableTypes: ['text', 'number'] },
          ]}
        />
      ),
      cell: ({ row }) => {
        const group = row.original
        const staticMembers = group.static || []
        const dynamicFilter = group.dynamic
        
        return (
          <div className="max-w-xs space-y-1">
            {staticMembers.length > 0 && (
              <div>
                <span className="text-xs font-medium text-gray-500">Static:</span>
                <div className="text-sm">
                  {staticMembers.slice(0, 2).join(', ')}
                  {staticMembers.length > 2 && ` +${staticMembers.length - 2} more`}
                </div>
              </div>
            )}
            {dynamicFilter && (
              <div>
                <span className="text-xs font-medium text-gray-500">Dynamic:</span>
                <code className="text-xs bg-gray-100 px-1 py-0.5 rounded block mt-1 truncate">
                  {typeof dynamicFilter === 'string' ? dynamicFilter : JSON.stringify(dynamicFilter)}
                </code>
              </div>
            )}
            {staticMembers.length === 0 && !dynamicFilter && (
              <span className="text-gray-400 text-sm italic">No members or filter</span>
            )}
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
          field="parent-device-group,parent-template,parent-vsys"
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
      accessorKey: 'tag',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Tags"
          field="tag"
          filters={filters}
          onFiltersChange={handleFiltersChange}
          filterOperators={[
            { value: 'contains', label: 'Contains', requiresValue: true, applicableTypes: ['text'] },
            { value: 'in', label: 'In List', requiresValue: true, applicableTypes: ['text'] },
            { value: 'not_in', label: 'Not In List', requiresValue: true, applicableTypes: ['text'] },
          ]}
        />
      ),
      cell: ({ row }) => {
        const group = row.original
        const tags = group.tag || []
        return (
          <div className="max-w-xs">
            {tags.length > 0 ? (
              <div className="flex flex-wrap gap-1">
                {tags.slice(0, 2).map((tag, index) => (
                  <span 
                    key={index}
                    className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                  >
                    {tag}
                  </span>
                ))}
                {tags.length > 2 && (
                  <span className="text-xs text-gray-500">
                    +{tags.length - 2} more
                  </span>
                )}
              </div>
            ) : (
              <span className="text-gray-400 text-sm italic">No tags</span>
            )}
          </div>
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
          <h2 className="text-lg font-bold tracking-tight">Address Groups</h2>
          <p className="text-muted-foreground">
            Manage groups of network addresses
          </p>
        </div>
        
        <DataTable
          columns={columns}
          data={displayData}
          pageCount={data?.total_pages}
          pagination={pagination}
          onPaginationChange={setPagination}
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