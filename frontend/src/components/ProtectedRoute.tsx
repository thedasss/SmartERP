/**
 * ProtectedRoute — redirects unauthenticated users to /login.
 */
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/features/auth/authStore'

interface Props {
  children: React.ReactNode
  requiredPermission?: string
}

export default function ProtectedRoute({ children, requiredPermission }: Props) {
  const { isAuthenticated, hasPermission } = useAuthStore()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-dark-100">Access Denied</h2>
          <p className="text-dark-400 mt-2">
            You don't have permission to view this page.
          </p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
