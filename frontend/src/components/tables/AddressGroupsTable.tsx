import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { configApi } from '@/services/api'
import { useConfigStore } from '@/stores/configStore'
import { AddressGroup, ColumnFilter } from '@/types/api'
import { Eye, MoreHorizontal } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DetailModal } from '@/components/modals/DetailModal'

export function AddressGroupsTable() {
  const { selectedConfig, updateStat } = useConfigStore()
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 })
  const [filters] = useState<ColumnFilter[]>([])
  const [detailItem, setDetailItem] = useState<AddressGroup | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['address-groups', selectedConfig?.name, pagination, filters],
    queryFn: async () => {
      if (!selectedConfig) return null
      const response = await configApi.getAddressGroups(
        selectedConfig.name,
        pagination.pageIndex + 1,
        pagination.pageSize,
        filters
      )
      updateStat('address-groups', response.total)
      return response
    },
    enabled: !!selectedConfig,
  })

  const columns: ColumnDef<AddressGroup>[] = [
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
    },
    {
      accessorKey: 'members',
      header: 'Members',
      cell: ({ row }) => {
        const members = row.getValue('members') as string[]
        return (
          <div className="max-w-xs">
            {members.length > 0 ? (
              <span className="text-sm">
                {members.slice(0, 3).join(', ')}
                {members.length > 3 && ` +${members.length - 3} more`}
              </span>
            ) : (
              <span className="text-gray-400 text-sm italic">No members</span>
            )}
          </div>
        )
      },
    },
    {
      accessorKey: 'location',
      header: 'Location',
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
          <h2 className="text-2xl font-bold tracking-tight">Address Groups</h2>
          <p className="text-muted-foreground">
            Manage groups of network addresses
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