import client from './client'
import type { Supplier, Customer } from '@/types'

export const partnerApi = {
  // Suppliers
  getSuppliers: async (): Promise<Supplier[]> => {
    const response = await client.get('/partners/suppliers')
    return response.data
  },
  
  createSupplier: async (data: Partial<Supplier>): Promise<Supplier> => {
    const response = await client.post('/partners/suppliers', data)
    return response.data
  },

  updateSupplier: async (id: string, data: Partial<Supplier>): Promise<Supplier> => {
    const response = await client.put(`/partners/suppliers/${id}`, data)
    return response.data
  },

  deleteSupplier: async (id: string): Promise<void> => {
    await client.delete(`/partners/suppliers/${id}`)
  },

  // Customers
  getCustomers: async (): Promise<Customer[]> => {
    const response = await client.get('/partners/customers')
    return response.data
  },

  createCustomer: async (data: Partial<Customer>): Promise<Customer> => {
    const response = await client.post('/partners/customers', data)
    return response.data
  },

  updateCustomer: async (id: string, data: Partial<Customer>): Promise<Customer> => {
    const response = await client.put(`/partners/customers/${id}`, data)
    return response.data
  },

  deleteCustomer: async (id: string): Promise<void> => {
    await client.delete(`/partners/customers/${id}`)
  }
}
