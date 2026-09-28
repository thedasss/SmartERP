import React, { useState, useEffect } from 'react';
import type { PurchaseOrder } from '../../services/procurementApi';
import type { Warehouse } from '@/types';
import { procurementApi } from '../../services/procurementApi';
import { inventoryApi } from '../../api/inventoryApi';

interface ReceiveGoodsModalProps {
  po: PurchaseOrder;
  onClose: () => void;
  onSuccess: () => void;
}

export const ReceiveGoodsModal: React.FC<ReceiveGoodsModalProps> = ({ po, onClose, onSuccess }) => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [warehouseId, setWarehouseId] = useState('');
  const [notes, setNotes] = useState('');
  const [receivingItems, setReceivingItems] = useState<{ po_item_id: string; quantity_received: number }[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const whs = await inventoryApi.getWarehouses();
        setWarehouses(whs);
        
        // Initialize receiving quantities with max remaining
        const initialItems = po.items
          .filter(item => (item.quantity - item.received_quantity) > 0)
          .map(item => ({
            po_item_id: item.id,
            quantity_received: item.quantity - item.received_quantity
          }));
        setReceivingItems(initialItems);
      } catch (err) {
        console.error('Failed to fetch warehouses', err);
      }
    };
    fetchData();
  }, [po]);

  const handleQuantityChange = (poItemId: string, value: string) => {
    setReceivingItems(prev => prev.map(item => 
      item.po_item_id === poItemId 
        ? { ...item, quantity_received: Number(value) } 
        : item
    ));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!warehouseId || receivingItems.length === 0) return;

    try {
      await procurementApi.receiveGoods(po.id, {
        warehouse_id: warehouseId,
        notes,
        items: receivingItems.filter(i => i.quantity_received > 0)
      });
      onSuccess();
    } catch (err) {
      console.error('Failed to receive goods', err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Receive Goods - {po.po_number}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Destination Warehouse</label>
            <select
              value={warehouseId}
              onChange={(e) => setWarehouseId(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500"
            >
              <option value="">Select a warehouse...</option>
              {warehouses.map(w => (
                <option key={w.id} value={w.id}>{w.name} ({w.code})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Receipt Notes (Optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500"
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Items to Receive</label>
            <div className="space-y-3">
              {po.items.map((item) => {
                const remaining = item.quantity - item.received_quantity;
                if (remaining <= 0) return null;
                
                const recItem = receivingItems.find(r => r.po_item_id === item.id);
                
                return (
                  <div key={item.id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg border border-gray-200">
                    <div>
                        <div className="font-medium text-gray-800">{item.product?.name || 'Unknown Product'}</div>
                        <div className="text-sm text-gray-500">Ordered: {item.quantity} | Received: {item.received_quantity}</div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">Receive Qty:</span>
                        <input
                            type="number"
                            min="0"
                            max={remaining}
                            step="0.01"
                            value={recItem?.quantity_received || 0}
                            onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                            className="w-24 border border-gray-300 rounded-md px-3 py-1.5 focus:ring-2 focus:ring-green-500"
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
              disabled={receivingItems.length === 0}
              className="px-5 py-2.5 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              Confirm Receipt
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
