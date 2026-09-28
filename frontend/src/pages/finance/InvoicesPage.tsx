import React, { useState, useEffect } from 'react';
import type { Invoice } from '../../services/financeApi';
import { financeApi } from '../../services/financeApi';
import { CreatePaymentModal } from './CreatePaymentModal';
import { formatCurrency } from '../../utils/formatters';

export const InvoicesPage: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [payingInvoice, setPayingInvoice] = useState<Invoice | null>(null);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const data = await financeApi.getInvoices();
      setInvoices(data);
    } catch (err) {
      console.error('Failed to fetch Invoices', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleSendReminder = async (invoiceId: string) => {
    try {
      await financeApi.sendReminder(invoiceId);
      alert("Reminder email sent successfully!");
    } catch (err) {
      console.error("Failed to send reminder", err);
      alert("Failed to send reminder.");
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DRAFT': return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-medium">Draft</span>;
      case 'ISSUED': return <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">Issued</span>;
      case 'PARTIALLY_PAID': return <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">Partial</span>;
      case 'PAID': return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">Paid</span>;
      case 'CANCELLED': return <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">Cancelled</span>;
      default: return null;
    }
  };

  const getTypeBadge = (type: string) => {
    return type === 'RECEIVABLE' 
        ? <span className="bg-emerald-50 text-emerald-700 px-2 py-1 rounded text-xs font-medium border border-emerald-200">Receivable</span>
        : <span className="bg-orange-50 text-orange-700 px-2 py-1 rounded text-xs font-medium border border-orange-200">Payable</span>;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-gray-500 mt-1">Manage receivables, payables, and record payments</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : invoices.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
          <div className="text-gray-400 mb-4 text-5xl">📄</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Invoices Found</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            You don't have any invoices yet.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="p-4 text-sm font-semibold text-gray-600">Invoice Number</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Type</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Date</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Total Amount</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Balance Due</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Status</th>
                  <th className="p-4 text-sm font-semibold text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {invoices.map((inv) => {
                  const balanceDue = inv.total_amount - inv.amount_paid;
                  return (
                  <tr key={inv.id} className="hover:bg-gray-50 transition-colors">
                    <td className="p-4 text-sm font-medium text-gray-900">{inv.invoice_number}</td>
                    <td className="p-4 text-sm">{getTypeBadge(inv.type)}</td>
                    <td className="p-4 text-sm text-gray-600">{new Date(inv.created_at).toLocaleDateString()}</td>
                    <td className="p-4 text-sm font-medium text-gray-900">{formatCurrency(inv.total_amount)}</td>
                    <td className="p-4 text-sm font-medium text-indigo-600">{formatCurrency(balanceDue)}</td>
                    <td className="p-4 text-sm">{getStatusBadge(inv.status)}</td>
                    <td className="p-4 text-sm flex gap-2">
                        {(inv.status === 'ISSUED' || inv.status === 'PARTIALLY_PAID') && (
                            <>
                              <button
                                  onClick={() => setPayingInvoice(inv)}
                                  className="text-indigo-600 hover:text-indigo-800 font-medium bg-indigo-50 px-3 py-1 rounded-md"
                              >
                                  Record Payment
                              </button>
                              <button
                                  onClick={() => handleSendReminder(inv.id)}
                                  className="text-orange-600 hover:text-orange-800 font-medium bg-orange-50 px-3 py-1 rounded-md"
                              >
                                  Send Reminder
                              </button>
                            </>
                        )}
                        <button
                            onClick={() => financeApi.downloadInvoicePdf(inv.id, inv.invoice_number)}
                            className="text-gray-600 hover:text-gray-800 font-medium bg-gray-100 px-3 py-1 rounded-md"
                        >
                            Download PDF
                        </button>
                    </td>
                  </tr>
                )})}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {payingInvoice && (
          <CreatePaymentModal
            invoice={payingInvoice}
            onClose={() => setPayingInvoice(null)}
            onSuccess={() => {
                setPayingInvoice(null);
                fetchInvoices();
            }}
          />
      )}
    </div>
  );
};
