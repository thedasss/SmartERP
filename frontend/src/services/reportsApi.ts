import { api } from './api';

export interface SalesTrendData {
  date: string;
  total_sales: number;
}

export interface InventoryValuationData {
  category_name: string;
  total_value: number;
}

export interface CashFlowData {
  date: string;
  money_in: number;
  money_out: number;
}

export const reportsApi = {
  getSalesTrend: async (): Promise<SalesTrendData[]> => {
    const { data } = await api.get('/reports/sales/trend');
    return data.data;
  },

  getInventoryValuation: async (): Promise<InventoryValuationData[]> => {
    const { data } = await api.get('/reports/inventory/valuation');
    return data.data;
  },

  getCashFlow: async (): Promise<CashFlowData[]> => {
    const { data } = await api.get('/reports/finance/cashflow');
    return data.data;
  }
};
