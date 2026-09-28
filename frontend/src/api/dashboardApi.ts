import apiClient from './client'

export interface DashboardActivity {
  id: string;
  type: 'sale' | 'purchase' | 'invoice' | 'inventory';
  description: string;
  amount?: number;
  timestamp: string;
}

export interface DashboardStats {
  sales: { total: number; change: string }
  purchases: { total: number; change: string }
  invoices: { outstanding: number; change: string }
  inventory: { value: number; items_count: number }
  recent_activities: DashboardActivity[]
}

export const dashboardApi = {
  getStats: async () => {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats')
    return response.data
  },
}
