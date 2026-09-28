import { api } from './api';

export interface SalesOrderItem {
  id: string;
  so_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  shipped_quantity: number;
  product?: {
    id: string;
    name: string;
    sku: string;
  };
}

export interface SalesOrder {
  id: string;
  company_id: string;
  so_number: string;
  customer_id: string;
  status: 'DRAFT' | 'CONFIRMED' | 'PARTIALLY_SHIPPED' | 'SHIPPED' | 'CANCELLED';
  total_amount: number;
  notes?: string;
  created_at: string;
  items: SalesOrderItem[];
  customer?: {
    id: string;
    name: string;
    email: string;
  };
}

export interface SalesOrderCreate {
  customer_id: string;
  notes?: string;
  items: {
    product_id: string;
    quantity: number;
    unit_price: number;
  }[];
}

export interface ShipmentItemCreate {
  so_item_id: string;
  quantity_shipped: number;
}

export interface ShipmentCreate {
  warehouse_id: string;
  notes?: string;
  items: ShipmentItemCreate[];
}

export const salesApi = {
  getSalesOrders: async (): Promise<SalesOrder[]> => {
    const { data } = await api.get('/sales/orders');
    return data;
  },

  createSalesOrder: async (payload: SalesOrderCreate): Promise<SalesOrder> => {
    const { data } = await api.post('/sales/orders', payload);
    return data;
  },

  shipGoods: async (soId: string, payload: ShipmentCreate): Promise<any> => {
    const { data } = await api.post(`/sales/orders/${soId}/ship`, payload);
    return data;
  }
};
