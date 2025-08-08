import { ApiStats } from '@/types/api'
import { useApiStatsStore } from '@/stores/apiStatsStore'
import { ChevronUp, ChevronDown, Activity, Clock, Database } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ApiStatsWidgetProps {
  stats: ApiStats[]
}

export function ApiStatsWidget({ stats }: ApiStatsWidgetProps) {
  const { isCollapsed, toggleCollapsed } = useApiStatsStore()

  if (stats.length === 0) return null

  const latestStats = stats.slice(-5).reverse()

  return (
    <div className={cn(
      "fixed bottom-0 right-4 bg-white border border-gray-200 rounded-t-lg shadow-lg transition-all duration-300",
      isCollapsed ? "h-12" : "h-64"
    )}>
      {/* Header */}
      <button
        onClick={toggleCollapsed}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-blue-600" />
          <span className="font-medium text-sm">API Statistics</span>
          {isCollapsed && stats.length > 0 && (
            <span className="text-xs text-gray-500">
              ({stats[0].query_time}ms)
            </span>
          )}
        </div>
        {isCollapsed ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {/* Content */}
      {!isCollapsed && (
        <div className="px-4 pb-4 overflow-y-auto h-52">
          <div className="space-y-3">
            {latestStats.map((stat, index) => (
              <div
                key={`${stat.endpoint}-${stat.timestamp}-${index}`}
                className="border-l-2 border-blue-500 pl-3 py-2"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {stat.endpoint}
                    </p>
                    <div className="flex items-center gap-4 mt-1">
                      <span className="flex items-center gap-1 text-xs text-gray-600">
                        <Clock className="h-3 w-3" />
                        {stat.query_time}ms
                      </span>
                      <span className="flex items-center gap-1 text-xs text-gray-600">
                        <Database className="h-3 w-3" />
                        {stat.items_retrieved} items
                      </span>
                    </div>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(stat.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}