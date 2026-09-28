import { api } from './api';

export interface Payment {
  id: string;
  invoice_id: string;
  amount: number;
  payment_date: string;
  reference_number?: string;
  notes?: string;
  created_at: string;
}

export interface Invoice {
  id: string;
  company_id: string;
  partner_id: string;
  reference_id?: string;
  invoice_number: string;
  type: 'RECEIVABLE' | 'PAYABLE';
  status: 'DRAFT' | 'ISSUED' | 'PARTIALLY_PAID' | 'PAID' | 'CANCELLED';
  total_amount: number;
  amount_paid: number;
  due_date?: string;
  notes?: string;
  created_at: string;
  payments: Payment[];
}

export interface InvoiceCreate {
  partner_id: string;
  reference_id?: string;
  type: 'RECEIVABLE' | 'PAYABLE';
  total_amount: number;
  due_date?: string;
  notes?: string;
}

export interface PaymentCreate {
  amount: number;
  payment_date: string;
  reference_number?: string;
  notes?: string;
}

export const financeApi = {
  getInvoices: async (): Promise<Invoice[]> => {
    const { data } = await api.get('/finance/invoices');
    return data;
  },

  createInvoice: async (payload: InvoiceCreate): Promise<Invoice> => {
    const { data } = await api.post('/finance/invoices', payload);
    return data;
  },

  recordPayment: async (invoiceId: string, payload: PaymentCreate): Promise<Payment> => {
    const { data } = await api.post(`/finance/invoices/${invoiceId}/payments`, payload);
    return data;
  },

  sendReminder: async (invoiceId: string): Promise<{success: boolean, message: string}> => {
    const { data } = await api.post(`/finance/invoices/${invoiceId}/remind`);
    return data;
  },

  downloadInvoicePdf: async (invoiceId: string, invoiceNumber: string): Promise<void> => {
    const { data } = await api.get(`/finance/invoices/${invoiceId}/pdf`, {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Invoice_${invoiceNumber}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.parentNode?.removeChild(link);
  }
};
