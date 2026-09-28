import React, { useState, useEffect } from 'react';
import type { SalesOrder } from '../../services/salesApi';
import { salesApi } from '../../services/salesApi';
import { CreateSOModal } from './CreateSOModal';
import { ShipGoodsModal } from './ShipGoodsModal';
import { formatCurrency } from '../../utils/formatters';

export const SalesOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [shippingSO, setShippingSO] = useState<SalesOrder | null>(null);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const data = await salesApi.getSalesOrders();
      setOrders(data);
    } catch (err) {
      console.error('Failed to fetch SOs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DRAFT': return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-medium">Draft</span>;
      case 'CONFIRMED': return <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">Confirmed</span>;
      case 'PARTIALLY_SHIPPED': return <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">Partial</span>;
      case 'SHIPPED': return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">Shipped</span>;
      case 'CANCELLED': return <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">Cancelled</span>;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sales Orders</h1>
          <p className="text-gray-500 mt-1">Manage sales and ship goods to customers</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm font-medium"
        >
          Create SO
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : orders.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
          <div className="text-gray-400 mb-4 text-5xl">📦</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Sales Orders Found</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            You haven't created any sales orders yet. Create one to start selling goods.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="p-4 text-sm font-semibold text-gray-600">SO Number</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Date</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Customer</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Total Amount</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Status</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {orders.map((so) => (
                  <tr key={so.id} className="hover:bg-gray-50 transition-colors">
                    <td className="p-4 text-sm font-medium text-gray-900">{so.so_number}</td>
                    <td className="p-4 text-sm text-gray-600">{new Date(so.created_at).toLocaleDateString()}</td>
                    <td className="p-4 text-sm text-gray-600">{so.customer?.name || 'Unknown Customer'}</td>
                    <td className="p-4 text-sm font-medium text-gray-900">{formatCurrency(so.total_amount)}</td>
                    <td className="p-4 text-sm">{getStatusBadge(so.status)}</td>
                    <td className="p-4 text-sm">
                        {(so.status === 'CONFIRMED' || so.status === 'PARTIALLY_SHIPPED') && (
                            <button
                                onClick={() => setShippingSO(so)}
                                className="text-blue-600 hover:text-blue-800 font-medium bg-blue-50 px-3 py-1 rounded-md"
                            >
                                Ship Goods
                            </button>
                        )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showCreateModal && (
        <CreateSOModal 
            onClose={() => setShowCreateModal(false)}
            onSuccess={() => {
                setShowCreateModal(false);
                fetchOrders();
            }}
        />
      )}

      {shippingSO && (
          <ShipGoodsModal
            so={shippingSO}
            onClose={() => setShippingSO(null)}
            onSuccess={() => {
                setShippingSO(null);
                fetchOrders();
            }}
          />
      )}
    </div>
  );
};
