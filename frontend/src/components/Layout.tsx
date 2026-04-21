import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { 
  LayoutDashboard, 
  Users, 
  AlertTriangle, 
  FileText, 
  LogOut,
  Bell
} from 'lucide-react'
import { cn } from '@/utils/helpers'

export default function Layout() {
  const { user, perfil, signOut } = useAuth()
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Estudiantes', href: '/estudiantes', icon: Users },
    { name: 'Alertas', href: '/alertas', icon: AlertTriangle },
    { name: 'Reportes', href: '/reportes', icon: FileText },
  ]

  const handleSignOut = async () => {
    await signOut()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-primary-600">
                Sistema de Análisis Académico
              </h1>
              <span className="ml-4 text-sm text-gray-500">
                IE Dos de Mayo - Chincha
              </span>
            </div>
            
            <div className="flex items-center gap-4">
              <button className="relative p-2 text-gray-400 hover:text-gray-600">
                <Bell className="w-5 h-5" />
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500"></span>
              </button>
              
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {perfil?.nombres} {perfil?.apellidos}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">{perfil?.rol}</p>
                </div>
                <button
                  onClick={handleSignOut}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Cerrar sesión"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Sidebar + Content */}
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
          <nav className="p-4 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname.startsWith(item.href)
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
