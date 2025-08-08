import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface DetailModalProps {
  item: any
  onClose: () => void
}

export function DetailModal({ item, onClose }: DetailModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">Object Details</h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="p-4 overflow-auto max-h-[calc(80vh-4rem)]">
          <pre className="bg-gray-50 p-4 rounded-lg overflow-auto">
            <code>{JSON.stringify(item, null, 2)}</code>
          </pre>
        </div>
      </div>
    </div>
  )
}