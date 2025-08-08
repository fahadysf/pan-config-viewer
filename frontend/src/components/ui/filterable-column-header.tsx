import { Column } from '@tanstack/react-table'
import { ArrowUpDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ColumnFilter } from '@/components/ui/column-filter'
import { ColumnFilter as ColumnFilterType, FilterOperator } from '@/types/api'

interface FilterableColumnHeaderProps<TData, TValue> {
  column: Column<TData, TValue>
  title: string
  field: string
  filters: ColumnFilterType[]
  onFiltersChange: (filters: ColumnFilterType[]) => void
  filterOperators?: FilterOperator[]
}

export function FilterableColumnHeader<TData, TValue>({
  column,
  title,
  field,
  filters,
  onFiltersChange,
  filterOperators,
}: FilterableColumnHeaderProps<TData, TValue>) {
  const currentFilter = filters.find(f => f.field === field)

  const handleFilterChange = (filter: ColumnFilterType | null) => {
    const newFilters = filters.filter(f => f.field !== field)
    if (filter) {
      newFilters.push(filter)
    }
    onFiltersChange(newFilters)
  }

  return (
    <div className="flex items-center justify-between">
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        className="h-auto p-0 font-medium hover:bg-transparent"
      >
        {title}
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
      <ColumnFilter
        field={field}
        currentFilter={currentFilter}
        onFilterChange={handleFilterChange}
        operators={filterOperators}
      />
    </div>
  )
}