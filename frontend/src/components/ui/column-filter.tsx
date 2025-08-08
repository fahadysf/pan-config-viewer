import { useState } from 'react'
import { Filter, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { ColumnFilter as ColumnFilterType, FilterOperator } from '@/types/api'

const FILTER_OPERATORS: FilterOperator[] = [
  { value: 'eq', label: 'Equals', requiresValue: true, applicableTypes: ['text', 'number'] },
  { value: 'contains', label: 'Contains', requiresValue: true, applicableTypes: ['text'] },
  { value: 'starts_with', label: 'Starts with', requiresValue: true, applicableTypes: ['text'] },
  { value: 'ends_with', label: 'Ends with', requiresValue: true, applicableTypes: ['text'] },
  { value: 'gt', label: 'Greater than', requiresValue: true, applicableTypes: ['number'] },
  { value: 'gte', label: 'Greater than or equal', requiresValue: true, applicableTypes: ['number'] },
  { value: 'lt', label: 'Less than', requiresValue: true, applicableTypes: ['number'] },
  { value: 'lte', label: 'Less than or equal', requiresValue: true, applicableTypes: ['number'] },
  { value: 'regex', label: 'Regex', requiresValue: true, applicableTypes: ['text'] },
]

interface ColumnFilterProps {
  field: string
  currentFilter?: ColumnFilterType
  onFilterChange: (filter: ColumnFilterType | null) => void
  operators?: FilterOperator[]
}

export function ColumnFilter({
  field,
  currentFilter,
  onFilterChange,
  operators = FILTER_OPERATORS,
}: ColumnFilterProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [operator, setOperator] = useState(currentFilter?.operator || 'contains')
  const [value, setValue] = useState(currentFilter?.value || '')

  const handleApply = () => {
    const selectedOperator = operators.find(op => op.value === operator)
    if (selectedOperator?.requiresValue && !value.trim()) {
      return
    }

    onFilterChange({
      field,
      operator,
      value: value.trim(),
    })
    setIsOpen(false)
  }

  const handleClear = () => {
    setValue('')
    setOperator('contains')
    onFilterChange(null)
    setIsOpen(false)
  }

  const isActive = !!currentFilter

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className={`h-6 w-6 p-0 ${
            isActive ? 'text-blue-600 bg-blue-50' : 'text-gray-400 hover:text-gray-600'
          }`}
        >
          <Filter className="h-3 w-3" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="start">
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Operator</label>
            <Select value={operator} onValueChange={setOperator}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {operators.map((op) => (
                  <SelectItem key={op.value} value={op.value}>
                    {op.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {operators.find(op => op.value === operator)?.requiresValue && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Value</label>
              <Input
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Enter filter value..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleApply()
                  }
                }}
              />
            </div>
          )}

          <div className="flex justify-between">
            <Button
              variant="outline"
              size="sm"
              onClick={handleClear}
              className="flex items-center gap-1"
            >
              <X className="h-3 w-3" />
              Clear
            </Button>
            <Button size="sm" onClick={handleApply}>
              Apply
            </Button>
          </div>

          {isActive && (
            <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
              Active filter: {currentFilter?.operator} "{currentFilter?.value}"
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}