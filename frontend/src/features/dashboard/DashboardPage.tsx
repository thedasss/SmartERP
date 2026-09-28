/**
 * Dashboard homepage — ERP overview with KPI cards and quick stats.
 */
import { useState, useEffect } from 'react'
import {
  TrendingUp, Package, ShoppingCart, FileText,
  AlertTriangle, Clock, ArrowUpRight,
} from 'lucide-react'
import { useAuthStore } from '@/features/auth/authStore'
import { dashboardApi, type DashboardStats } from '@/api/dashboardApi'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  
  useEffect(() => {
    dashboardApi.getStats().then(setStats).catch(console.error)
  }, [])

  const statCards = [
    { label: 'Total Sales', value: `$${stats?.sales.total.toFixed(2) || '0.00'}`, change: stats?.sales.change || '+0%', icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-500/10' },
    { label: 'Total Purchases', value: `$${stats?.purchases.total.toFixed(2) || '0.00'}`, change: stats?.purchases.change || '+0%', icon: ShoppingCart, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { label: 'Outstanding Invoices', value: `${stats?.invoices.outstanding || 0}`, change: stats?.invoices.change || '0 overdue', icon: FileText, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    { label: 'Inventory Value', value: `$${stats?.inventory.value.toFixed(2) || '0.00'}`, change: `${stats?.inventory.items_count || 0} products`, icon: Package, color: 'text-primary-400', bg: 'bg-primary-500/10' },
  ]

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-dark-50">
          Good morning, {user?.full_name.split(' ')[0] ?? 'there'} 👋
        </h1>
        <p className="text-dark-400 text-sm mt-1">
          Here's what's happening with your business today.
        </p>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon
          return (
            <div key={card.label} className="card-hover">
              <div className="flex items-start justify-between">
                <div>
                  <p className="stat-label">{card.label}</p>
                  <p className="stat-value mt-2">{card.value}</p>
                  <p className="text-xs text-dark-400 mt-1">{card.change}</p>
                </div>
                <div className={`p-2.5 rounded-xl ${card.bg}`}>
                  <Icon className={`w-5 h-5 ${card.color}`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Middle row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent activity */}
        <div className="lg:col-span-2 card">
          <h3 className="text-sm font-semibold text-dark-200 mb-4">Recent Activity</h3>
          {stats?.recent_activities && stats.recent_activities.length > 0 ? (
            <div className="space-y-4">
              {stats.recent_activities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-dark-800 transition-colors">
                  <div className="p-2 rounded-full bg-dark-700 flex-shrink-0">
                    {activity.type === 'sale' && <TrendingUp className="w-4 h-4 text-green-400" />}
                    {activity.type === 'purchase' && <ShoppingCart className="w-4 h-4 text-blue-400" />}
                    {activity.type === 'invoice' && <FileText className="w-4 h-4 text-yellow-400" />}
                    {activity.type === 'inventory' && <Package className="w-4 h-4 text-primary-400" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-dark-100 truncate">{activity.description}</p>
                    <p className="text-xs text-dark-400 mt-1">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                  {activity.amount !== undefined && (
                    <div className="text-sm font-semibold text-dark-50">
                      ${activity.amount.toFixed(2)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Clock className="w-10 h-10 text-dark-600 mb-3" />
              <p className="text-dark-400 text-sm">No recent activity</p>
              <p className="text-dark-500 text-xs mt-1">Activity will appear here as you use the system.</p>
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="card">
          <h3 className="text-sm font-semibold text-dark-200 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            {[
              { label: 'New Purchase Request', href: '/procurement/new' },
              { label: 'Add Product', href: '/inventory/new' },
              { label: 'Create Invoice', href: '/invoices/new' },
              { label: 'View Reports', href: '/reports' },
            ].map((action) => (
              <a
                key={action.label}
                href={action.href}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-dark-700
                           transition-colors duration-200 group"
              >
                <span className="text-sm text-dark-300 group-hover:text-dark-100">{action.label}</span>
                <ArrowUpRight className="w-3.5 h-3.5 text-dark-500 group-hover:text-primary-400 transition-colors" />
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts */}
      <div className="card border-yellow-500/20">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle className="w-4 h-4 text-yellow-400" />
          <h3 className="text-sm font-semibold text-dark-200">Alerts</h3>
        </div>
        <p className="text-dark-400 text-sm">No alerts at this time. The system is operating normally.</p>
      </div>
    </div>
  )
}
