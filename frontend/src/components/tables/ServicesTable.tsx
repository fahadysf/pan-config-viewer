import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { configApi } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import { Service, ColumnFilter } from '@/types/api'
import { Eye, MoreHorizontal } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { FilterableColumnHeader } from '@/components/ui/filterable-column-header'
import { DetailModal } from '@/components/modals/DetailModal'

export function ServicesTable() {
  const { selectedConfig, updateStat } = useConfigStore()
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
  const [filters, setFilters] = useState<ColumnFilter[]>([])
  const [detailItem, setDetailItem] = useState<Service | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['services', selectedConfig?.name, pagination, filters],
    queryFn: async () => {
      if (!selectedConfig) return null
      const response = await configApi.getServices(
        selectedConfig.name,
        pagination.pageIndex + 1,
        pagination.pageSize,
        filters
      )
      updateStat('services', response.total_items)
      return response
    },
    enabled: !!selectedConfig,
  })

  const columns: ColumnDef<Service>[] = [
    {
      accessorKey: 'name',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Name"
          field="name"
          filters={filters}
          onFiltersChange={setFilters}
        />
      ),
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue('name')}</div>
      ),
    },
    {
      accessorKey: 'protocol',
      header: ({ column }) => (
        <FilterableColumnHeader
          column={column}
          title="Protocol/Port"
          field="protocol"
          filters={filters}
          onFiltersChange={setFilters}
          filterOperators={[
            { value: 'contains', label: 'Contains', requiresValue: true, applicableTypes: ['text'] },
            { value: 'eq', label: 'Equals', requiresValue: true, applicableTypes: ['text', 'number'] },
            { value: 'gte', label: 'Port >= ', requiresValue: true, applicableTypes: ['number'] },
            { value: 'lte', label: 'Port <= ', requiresValue: true, applicableTypes: ['number'] },
          ]}
        />
      ),
      cell: ({ row }) => {
        const service = row.original
        const hasTcp = service.protocol?.tcp != null
        const hasUdp = service.protocol?.udp != null
        
        if (!hasTcp && !hasUdp) {
          return (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              No Protocol
            </span>
          )
        }
        
        return (
          <div className="space-y-1">
            {hasTcp && (
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  TCP
                </span>
                <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                  {service.protocol.tcp?.port || 'N/A'}
                </code>
                {service.protocol.tcp?.override && (
                  <span className="text-xs text-orange-600" title="Override enabled">⚠</span>
                )}
              </div>
            )}
            {hasUdp && (
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  UDP
                </span>
                <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                  {service.protocol.udp?.port || 'N/A'}
                </code>
                {service.protocol.udp?.override && (
                  <span className="text-xs text-orange-600" title="Override enabled">⚠</span>
                )}
              </div>
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
          onFiltersChange={setFilters}
        />
      ),
      cell: ({ row }) => {
        const service = row.original
        const location = service['parent-device-group'] || 
                        service['parent-template'] || 
                        service['parent-vsys'] || 
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
          onFiltersChange={setFilters}
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
        const service = row.original

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
              <DropdownMenuItem onClick={() => setDetailItem(service)}>
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
          <h2 className="text-2xl font-bold tracking-tight">Services</h2>
          <p className="text-muted-foreground">
            Manage network services and port configurations
          </p>
        </div>
        
        <DataTable
          columns={columns}
          data={data?.items || []}
          pageCount={data?.total_pages}
          pagination={pagination}
          onPaginationChange={setPagination}
          loading={isLoading}
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