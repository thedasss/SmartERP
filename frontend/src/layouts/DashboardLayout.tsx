/**
 * DashboardLayout — main ERP shell with sidebar, topbar, and content area.
 */
import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Package, ShoppingCart, TrendingUp,
  Users, Building2, FileText, BarChart3, Bot,
  Bell, LogOut, Menu, X, Zap, Warehouse, UserCheck,
  ChevronRight,
} from 'lucide-react'
import toast from 'react-hot-toast'

import { useAuthStore } from '@/features/auth/authStore'
import { authApi } from '@/api/auth'
import { ThemeToggle } from '@/components/ThemeToggle'

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/products', icon: Package, label: 'Products' },
  { to: '/procurement', icon: ShoppingCart, label: 'Procurement' },
  { to: '/sales', icon: TrendingUp, label: 'Sales' },
  { to: '/suppliers', icon: Building2, label: 'Suppliers' },
  { to: '/customers', icon: UserCheck, label: 'Customers' },
  { to: '/invoices', icon: FileText, label: 'Invoices' },
  { to: '/warehouses', icon: Warehouse, label: 'Warehouses' },
  { to: '/stock', icon: Package, label: 'Stock Levels' },
  { to: '/reports', icon: BarChart3, label: 'Reports' },
  { to: '/documents', icon: FileText, label: 'Documents' },
  { to: '/ai', icon: Bot, label: 'AI Assistant' },
  { to: '/users', icon: Users, label: 'Users' },
]

export default function DashboardLayout() {
  const { user, logout, refreshToken } = useAuthStore()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLogout = async () => {
    try {
      if (refreshToken) await authApi.logout(refreshToken)
    } catch {
      // ignore
    }
    logout()
    navigate('/login', { replace: true })
    toast.success('Signed out successfully')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-dark-950">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside
        className={`flex-shrink-0 flex flex-col bg-dark-900 border-r border-dark-700/50
          transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-16'}`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 h-16 border-b border-dark-700/50">
          <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
            <Zap className="w-4 h-4 text-white" />
          </div>
          {sidebarOpen && (
            <span className="font-bold text-white text-lg leading-none">SmartERP</span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                isActive ? 'nav-item-active' : 'nav-item'
              }
              title={!sidebarOpen ? label : undefined}
            >
              <Icon className="w-4.5 h-4.5 flex-shrink-0" size={18} />
              {sidebarOpen && <span className="flex-1">{label}</span>}
              {sidebarOpen && (
                <ChevronRight className="w-3.5 h-3.5 text-dark-600 opacity-0 group-hover:opacity-100" />
              )}
            </NavLink>
          ))}
        </nav>

        {/* User info */}
        {sidebarOpen && user && (
          <div className="p-3 border-t border-dark-700/50">
            <div className="flex items-center gap-3 p-2.5 rounded-lg bg-dark-800">
              <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-bold text-white">
                  {user.full_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-dark-100 truncate">{user.full_name}</p>
                <p className="text-xs text-dark-400 truncate">{user.email}</p>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* ── Main Content ─────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="h-16 bg-dark-900 border-b border-dark-700/50 flex items-center px-6 gap-4 flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="btn-ghost p-2 -ml-2"
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>

          <div className="flex-1" />

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Notifications */}
          <button className="btn-ghost relative p-2">
            <Bell size={18} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary-500" />
          </button>

          {/* Logout */}
          <button onClick={handleLogout} className="btn-ghost p-2" title="Sign out">
            <LogOut size={18} />
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6 bg-dark-950">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
