import client from './client'
import type { Product, ProductCategory } from '@/types'

export const productApi = {
  // Categories
  getCategories: async (): Promise<ProductCategory[]> => {
    const response = await client.get('/products/categories')
    return response.data
  },
  
  createCategory: async (data: Partial<ProductCategory>): Promise<ProductCategory> => {
    const response = await client.post('/products/categories', data)
    return response.data
  },

  updateCategory: async (id: string, data: Partial<ProductCategory>): Promise<ProductCategory> => {
    const response = await client.put(`/products/categories/${id}`, data)
    return response.data
  },

  deleteCategory: async (id: string): Promise<void> => {
    await client.delete(`/products/categories/${id}`)
  },

  // Products
  getProducts: async (): Promise<Product[]> => {
    const response = await client.get('/products')
    return response.data
  },

  createProduct: async (data: Partial<Product>): Promise<Product> => {
    const response = await client.post('/products', data)
    return response.data
  },

  updateProduct: async (id: string, data: Partial<Product>): Promise<Product> => {
    const response = await client.put(`/products/${id}`, data)
    return response.data
  },

  deleteProduct: async (id: string): Promise<void> => {
    await client.delete(`/products/${id}`)
  }
}
