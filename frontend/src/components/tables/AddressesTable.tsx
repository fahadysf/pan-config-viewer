import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { configApi } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import { Address, ColumnFilter } from '@/types/api'
import { Eye, MoreHorizontal } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DetailModal } from '@/components/modals/DetailModal'

export function AddressesTable() {
  const { selectedConfig, updateStat } = useConfigStore()
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 })
  const [filters] = useState<ColumnFilter[]>([])
  const [detailItem, setDetailItem] = useState<Address | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['addresses', selectedConfig?.name, pagination, filters],
    queryFn: async () => {
      if (!selectedConfig) return null
      const response = await configApi.getAddresses(
        selectedConfig.name,
        pagination.pageIndex + 1,
        pagination.pageSize,
        filters
      )
      updateStat('addresses', response.total_items)
      return response
    },
    enabled: !!selectedConfig,
  })

  const columns: ColumnDef<Address>[] = [
    {
      accessorKey: 'name',
      header: 'Name',
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue('name')}</div>
      ),
    },
    {
      accessorKey: 'type',
      header: 'Type',
      cell: ({ row }) => (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          {row.getValue('type')}
        </span>
      ),
    },
    {
      accessorKey: 'value',
      header: 'Value',
      cell: ({ row }) => {
        const address = row.original
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
      },
    },
    {
      accessorKey: 'location',
      header: 'Location',
      cell: ({ row }) => {
        const address = row.original
        const location = address['parent-device-group'] || 
                        address['parent-template'] || 
                        address['parent-vsys'] || 
                        'Shared'
        return <span className="text-sm">{location}</span>
      },
    },
    {
      accessorKey: 'description',
      header: 'Description',
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
              <DropdownMenuItem onClick={() => setDetailItem(address)}>
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