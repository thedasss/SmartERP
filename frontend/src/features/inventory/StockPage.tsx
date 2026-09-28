import { useState, useEffect } from 'react'
import { Package, ArrowRightLeft } from 'lucide-react'
import { inventoryApi } from '@/api/inventoryApi'
import type { StockItem } from '@/types'

export default function StockPage() {
  const [stockItems, setStockItems] = useState<StockItem[]>([])
  const [loading, setLoading] = useState(true)

  const fetchStock = async () => {
    try {
      setLoading(true)
      const data = await inventoryApi.getStockItems()
      setStockItems(data)
    } catch (error) {
      console.error('Failed to fetch stock', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStock()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-dark-50">Stock Levels</h1>
          <p className="text-dark-400 text-sm mt-1">Current inventory quantities across all warehouses.</p>
        </div>
        <button className="btn-secondary flex items-center gap-2">
          <ArrowRightLeft className="w-4 h-4" />
          Stock Adjustment
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="card p-4 flex items-center gap-4">
          <div className="p-3 bg-primary-500/10 text-primary-400 rounded-lg">
            <Package className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-dark-400">Total Stock Items</p>
            <p className="text-xl font-bold text-dark-100">{stockItems.length}</p>
          </div>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-dark-800/50 border-b border-dark-700">
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider">Product</th>
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider">SKU</th>
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider">Warehouse</th>
                <th className="p-4 text-xs font-semibold text-dark-300 uppercase tracking-wider text-right">Quantity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-700">
              {loading ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-dark-400">Loading stock data...</td>
                </tr>
              ) : stockItems.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-dark-400">No stock recorded yet.</td>
                </tr>
              ) : (
                stockItems.map((item) => (
                  <tr key={item.id} className="hover:bg-dark-700/50 transition-colors group">
                    <td className="p-4 text-sm text-dark-200 font-medium">{item.product?.name || 'Unknown'}</td>
                    <td className="p-4 text-sm text-dark-400">{item.product?.sku || '-'}</td>
                    <td className="p-4 text-sm text-dark-200">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-dark-600 text-dark-300">
                        {item.warehouse?.name || 'Unknown'}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-right font-medium text-dark-100">
                      {item.quantity} <span className="text-dark-500 font-normal text-xs ml-1">{item.product?.unit_of_measure}</span>
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
