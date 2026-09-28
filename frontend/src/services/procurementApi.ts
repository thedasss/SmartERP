import { api } from './api';

export interface PurchaseOrderItem {
  id: string;
  po_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  received_quantity: number;
  product?: any;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  status: string;
  total_amount: number;
  supplier_id: string;
  supplier?: any;
  items: PurchaseOrderItem[];
  created_at: string;
}

export interface PurchaseOrderCreate {
  supplier_id: string;
  notes?: string;
  items: { product_id: string; quantity: number; unit_price: number }[];
}

export interface GoodsReceiptCreate {
  warehouse_id: string;
  notes?: string;
  items: { po_item_id: string; quantity_received: number }[];
}

const API_URL = '/procurement';

export const procurementApi = {
  getPurchaseOrders: async (): Promise<PurchaseOrder[]> => {
    const response = await api.get(`${API_URL}/orders`);
    return response.data;
  },

  createPurchaseOrder: async (data: PurchaseOrderCreate): Promise<PurchaseOrder> => {
    const response = await api.post(`${API_URL}/orders`, data);
    return response.data;
  },

  receiveGoods: async (poId: string, data: GoodsReceiptCreate): Promise<any> => {
    const response = await api.post(`${API_URL}/orders/${poId}/receive`, data);
    return response.data;
  },
};
