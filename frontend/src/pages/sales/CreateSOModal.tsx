import React, { useState, useEffect } from 'react';
import type { Customer, Product } from '@/types';
import { partnerApi } from '../../api/partnerApi';
import { productApi } from '../../api/productApi';
import { salesApi } from '../../services/salesApi';

interface CreateSOModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateSOModal: React.FC<CreateSOModalProps> = ({ onClose, onSuccess }) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [customerId, setCustomerId] = useState('');
  const [notes, setNotes] = useState('');
  const [items, setItems] = useState<{ productId: string; quantity: number; unitPrice: number }[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [custs, prods] = await Promise.all([
          partnerApi.getCustomers(),
          productApi.getProducts()
        ]);
        setCustomers(custs);
        setProducts(prods);
      } catch (err) {
        console.error('Failed to fetch modal data', err);
      }
    };
    fetchData();
  }, []);

  const handleAddItem = () => {
    setItems([...items, { productId: '', quantity: 1, unitPrice: 0 }]);
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    const newItems = [...items];
    (newItems[index] as any)[field] = value;
    
    // Auto-fill price if product is selected
    if (field === 'productId') {
        const prod = products.find(p => p.id === value);
        if (prod) {
            newItems[index].unitPrice = Number(prod.price) || 0;
        }
    }
    setItems(newItems);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId || items.length === 0) return;

    try {
      await salesApi.createSalesOrder({
        customer_id: customerId,
        notes,
        items: items.map(i => ({
            product_id: i.productId,
            quantity: Number(i.quantity),
            unit_price: Number(i.unitPrice)
        }))
      });
      onSuccess();
    } catch (err) {
      console.error('Failed to create SO', err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Create Sales Order</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Customer</label>
            <select
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select a customer...</option>
              {customers.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
              rows={2}
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700">Order Items</label>
                <button type="button" onClick={handleAddItem} className="text-sm bg-indigo-50 text-indigo-600 px-3 py-1 rounded-md hover:bg-indigo-100">
                    + Add Item
                </button>
            </div>
            
            <div className="space-y-3">
              {items.map((item, index) => (
                <div key={index} className="flex gap-3 items-center bg-gray-50 p-3 rounded-lg border border-gray-100">
                  <select
                    value={item.productId}
                    onChange={(e) => handleItemChange(index, 'productId', e.target.value)}
                    required
                    className="flex-1 border border-gray-300 rounded-md px-3 py-1.5"
                  >
                    <option value="">Product...</option>
                    {products.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min="1"
                    step="0.01"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                    className="w-24 border border-gray-300 rounded-md px-3 py-1.5"
                    placeholder="Qty"
                    required
                  />
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={item.unitPrice}
                    onChange={(e) => handleItemChange(index, 'unitPrice', e.target.value)}
                    className="w-32 border border-gray-300 rounded-md px-3 py-1.5"
                    placeholder="Price"
                    required
                  />
                  <button type="button" onClick={() => setItems(items.filter((_, i) => i !== index))} className="text-red-500 hover:text-red-700 p-1">
                      ✕
                  </button>
                </div>
              ))}
              {items.length === 0 && (
                  <p className="text-sm text-gray-500 italic text-center py-4">No items added. Click "+ Add Item".</p>
              )}
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
              disabled={items.length === 0}
              className="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              Create Sales Order
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
