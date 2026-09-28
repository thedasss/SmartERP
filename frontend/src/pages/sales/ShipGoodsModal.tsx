import React, { useState, useEffect } from 'react';
import type { SalesOrder } from '../../services/salesApi';
import type { Warehouse } from '@/types';
import { salesApi } from '../../services/salesApi';
import { inventoryApi } from '../../api/inventoryApi';

interface ShipGoodsModalProps {
  so: SalesOrder;
  onClose: () => void;
  onSuccess: () => void;
}

export const ShipGoodsModal: React.FC<ShipGoodsModalProps> = ({ so, onClose, onSuccess }) => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [warehouseId, setWarehouseId] = useState('');
  const [notes, setNotes] = useState('');
  const [shippingItems, setShippingItems] = useState<{ so_item_id: string; quantity_shipped: number }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const whs = await inventoryApi.getWarehouses();
        setWarehouses(whs);
        
        // Initialize shipping quantities with max remaining
        const initialItems = so.items
          .filter(item => (item.quantity - item.shipped_quantity) > 0)
          .map(item => ({
            so_item_id: item.id,
            quantity_shipped: item.quantity - item.shipped_quantity
          }));
        setShippingItems(initialItems);
      } catch (err) {
        console.error('Failed to fetch warehouses', err);
      }
    };
    fetchData();
  }, [so]);

  const handleQuantityChange = (soItemId: string, value: string) => {
    setShippingItems(prev => prev.map(item => 
      item.so_item_id === soItemId 
        ? { ...item, quantity_shipped: Number(value) } 
        : item
    ));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!warehouseId || shippingItems.length === 0) return;
    setError(null);

    try {
      await salesApi.shipGoods(so.id, {
        warehouse_id: warehouseId,
        notes,
        items: shippingItems.filter(i => i.quantity_shipped > 0)
      });
      onSuccess();
    } catch (err: any) {
      console.error('Failed to ship goods', err);
      setError(err.response?.data?.detail || 'Failed to ship goods. Ensure sufficient stock.');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Ship Goods - {so.so_number}</h2>
        
        {error && (
            <div className="mb-4 bg-red-50 text-red-700 p-3 rounded-lg border border-red-100 text-sm">
                {error}
            </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Source Warehouse</label>
            <select
              value={warehouseId}
              onChange={(e) => setWarehouseId(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a warehouse...</option>
              {warehouses.map(w => (
                <option key={w.id} value={w.id}>{w.name} ({w.code})</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Items will be deducted from this warehouse's stock.</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Shipment Notes (Optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Items to Ship</label>
            <div className="space-y-3">
              {so.items.map((item) => {
                const remaining = item.quantity - item.shipped_quantity;
                if (remaining <= 0) return null;
                
                const shipItem = shippingItems.find(r => r.so_item_id === item.id);
                
                return (
                  <div key={item.id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg border border-gray-200">
                    <div>
                        <div className="font-medium text-gray-800">{item.product?.name || 'Unknown Product'}</div>
                        <div className="text-sm text-gray-500">Ordered: {item.quantity} | Shipped: {item.shipped_quantity}</div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">Ship Qty:</span>
                        <input
                            type="number"
                            min="0"
                            max={remaining}
                            step="0.01"
                            value={shipItem?.quantity_shipped || 0}
                            onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                            className="w-24 border border-gray-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-8">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={shippingItems.length === 0}
              className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Confirm Shipment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
