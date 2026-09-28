import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2 } from 'lucide-react'
import { inventoryApi } from '@/api/inventoryApi'
import type { Warehouse } from '@/types'

export default function WarehousesPage() {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [loading, setLoading] = useState(true)

  const fetchWarehouses = async () => {
    try {
      setLoading(true)
      const data = await inventoryApi.getWarehouses()
      setWarehouses(data)
    } catch (error) {
      console.error('Failed to fetch warehouses', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWarehouses()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-dark-50">Warehouses</h1>
          <p className="text-dark-400 text-sm mt-1">Manage your physical and logical storage locations.</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Warehouse
        </button>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-dark-800/50 border-b border-dark-700">
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider">Code</th>
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider">Name</th>
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider">Location</th>
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider">Status</th>
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-700">
              {loading ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-dark-400">Loading warehouses...</td>
                </tr>
              ) : warehouses.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-dark-400">No warehouses found. Add one to get started.</td>
                </tr>
              ) : (
                warehouses.map((w) => (
                  <tr key={w.id} className="hover:bg-dark-700/50 transition-colors group">
                    <td className="p-4 text-sm text-dark-200 font-medium">{w.code}</td>
                    <td className="p-4 text-sm text-dark-200">{w.name}</td>
                    <td className="p-4 text-sm text-dark-400">{w.location || '-'}</td>
                    <td className="p-4 text-sm">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        w.is_active ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                      }`}>
                        {w.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-right space-x-2">
                      <button className="text-dark-400 hover:text-primary-400 transition-colors">
                        <Edit2 className="w-4 h-4 inline" />
                      </button>
                      <button className="text-dark-400 hover:text-red-400 transition-colors">
                        <Trash2 className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
