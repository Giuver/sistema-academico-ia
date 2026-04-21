import { Loader2 } from 'lucide-react'
import { cn } from '@/utils/helpers'

interface LoadingSpinnerProps {
  fullScreen?: boolean
  size?: 'sm' | 'md' | 'lg'
  message?: string
}

export default function LoadingSpinner({ 
  fullScreen = false, 
  size = 'md',
  message 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  const spinner = (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2 className={cn('animate-spin text-primary-600', sizeClasses[size])} />
      {message && <p className="text-sm text-gray-600">{message}</p>}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white flex items-center justify-center z-50">
        {spinner}
      </div>
    )
  }

  return spinner
}
