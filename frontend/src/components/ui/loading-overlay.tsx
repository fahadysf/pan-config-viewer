import { Loader2 } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'

interface LoadingOverlayProps {
  isLoading: boolean
  progress?: number
  message?: string
  className?: string
}

export function LoadingOverlay({ 
  isLoading, 
  progress = 0, 
  message = 'Loading...',
  className 
}: LoadingOverlayProps) {
  if (!isLoading) return null

  return (
    <div 
      className={cn(
        "absolute inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm",
        className
      )}
    >
      <div className="flex flex-col items-center gap-4 p-6 bg-white rounded-lg shadow-lg">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        
        <div className="text-center">
          <p className="text-sm font-medium text-gray-900">{message}</p>
          {progress > 0 && (
            <p className="text-xs text-gray-500 mt-1">{progress}% complete</p>
          )}
        </div>
        
        {progress > 0 && (
          <Progress value={progress} className="w-48" />
        )}
      </div>
    </div>
  )
}