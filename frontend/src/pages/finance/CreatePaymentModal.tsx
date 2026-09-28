import React, { useState } from 'react';
import type { Invoice } from '../../services/financeApi';
import { financeApi } from '../../services/financeApi';
import { formatCurrency } from '../../utils/formatters';

interface CreatePaymentModalProps {
  invoice: Invoice;
  onClose: () => void;
  onSuccess: () => void;
}

export const CreatePaymentModal: React.FC<CreatePaymentModalProps> = ({ invoice, onClose, onSuccess }) => {
  const remainingBalance = invoice.total_amount - invoice.amount_paid;
  
  const [amount, setAmount] = useState<number | string>(remainingBalance);
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split('T')[0]);
  const [referenceNumber, setReferenceNumber] = useState('');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    const payAmount = Number(amount);
    if (payAmount <= 0) {
        setError('Payment amount must be greater than zero.');
        return;
    }
    if (payAmount > remainingBalance) {
        setError(`Payment amount cannot exceed the remaining balance of ${formatCurrency(remainingBalance)}.`);
        return;
    }

    try {
      await financeApi.recordPayment(invoice.id, {
        amount: payAmount,
        payment_date: paymentDate,
        reference_number: referenceNumber,
        notes
      });
      onSuccess();
    } catch (err: any) {
      console.error('Failed to record payment', err);
      setError(err.response?.data?.detail || 'Failed to record payment. Please try again.');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Record Payment</h2>
        
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-100">
            <div className="text-sm text-gray-500 mb-1">Invoice {invoice.invoice_number}</div>
            <div className="flex justify-between items-center mb-1">
                <span className="font-medium text-gray-700">Total Amount:</span>
                <span className="font-medium">{formatCurrency(invoice.total_amount)}</span>
            </div>
            <div className="flex justify-between items-center mb-1">
                <span className="font-medium text-green-700">Amount Paid:</span>
                <span className="font-medium text-green-700">{formatCurrency(invoice.amount_paid)}</span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-gray-200 mt-2">
                <span className="font-bold text-gray-900">Remaining Balance:</span>
                <span className="font-bold text-indigo-600">{formatCurrency(remainingBalance)}</span>
            </div>
        </div>

        {error && (
            <div className="mb-4 bg-red-50 text-red-700 p-3 rounded-lg border border-red-100 text-sm">
                {error}
            </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Payment Amount</label>
            <input
              type="number"
              min="0.01"
              max={remainingBalance}
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Payment Date</label>
            <input
              type="date"
              value={paymentDate}
              onChange={(e) => setPaymentDate(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Reference Number (Optional)</label>
            <input
              type="text"
              value={referenceNumber}
              onChange={(e) => setReferenceNumber(e.target.value)}
              placeholder="e.g. Check #1234, Transfer ID"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
            />
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
              className="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
            >
              Record Payment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
