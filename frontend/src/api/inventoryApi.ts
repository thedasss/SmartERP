import apiClient from './client'
import type { Warehouse, StockItem, StockMovement } from '@/types'

export const inventoryApi = {
  // Warehouses
  getWarehouses: async (skip = 0, limit = 50) => {
    const response = await apiClient.get<Warehouse[]>('/inventory/warehouses', {
      params: { skip, limit },
    })
    return response.data
  },

  createWarehouse: async (data: Partial<Warehouse>) => {
    const response = await apiClient.post<Warehouse>('/inventory/warehouses', data)
    return response.data
  },

  updateWarehouse: async (id: string, data: Partial<Warehouse>) => {
    const response = await apiClient.put<Warehouse>(`/inventory/warehouses/${id}`, data)
    return response.data
  },

  deleteWarehouse: async (id: string) => {
    await apiClient.delete(`/inventory/warehouses/${id}`)
  },

  // Stock Items
  getStockItems: async (params?: { warehouse_id?: string; product_id?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<StockItem[]>('/inventory/stock', { params })
    return response.data
  },

  // Stock Movements
  getMovements: async (params?: { warehouse_id?: string; product_id?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<StockMovement[]>('/inventory/movements', { params })
    return response.data
  },

  recordMovement: async (data: {
    product_id: string
    warehouse_id: string
    movement_type: 'IN' | 'OUT' | 'TRANSFER'
    quantity: number
    reference?: string
    notes?: string
  }) => {
    const response = await apiClient.post<StockMovement>('/inventory/movements', data)
    return response.data
  },
}
