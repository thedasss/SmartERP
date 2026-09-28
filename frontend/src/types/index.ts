// TypeScript types for the SmartERP frontend

// ── Auth Types ────────────────────────────────────────────────

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface CurrentUser {
  id: string
  company_id: string
  email: string
  full_name: string
  is_active: boolean
  is_super_admin: boolean
  permissions: string[]
  roles: string[]
}

// ── User Types ────────────────────────────────────────────────

export interface User {
  id: string
  company_id: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  phone?: string
  avatar_url?: string
  is_active: boolean
  is_super_admin: boolean
  last_login_at?: string
  created_at: string
  roles: Role[]
}

export interface UserCreate {
  email: string
  password: string
  first_name: string
  last_name: string
  phone?: string
  role_ids: string[]
}

export interface UserUpdate {
  first_name?: string
  last_name?: string
  phone?: string
  is_active?: boolean
}

export interface Role {
  id: string
  name: string
  description?: string
  company_id?: string
  is_system: boolean
  created_at: string
  permissions: Permission[]
}

export interface Permission {
  id: string
  name: string
  description?: string
  module: string
  action: string
  created_at: string
}

// ── Product Types ─────────────────────────────────────────────

export interface ProductCategory {
  id: string
  company_id: string
  name: string
  description?: string
  is_active: boolean
}

export interface Product {
  id: string
  company_id: string
  category_id?: string
  category?: ProductCategory
  sku: string
  name: string
  description?: string
  price: string | number
  cost: string | number
  unit_of_measure: string
  min_stock_level: string | number
  is_active: boolean
}

// ── Partner Types (Customers & Suppliers) ──────────────────────

export interface Partner {
  id: string
  company_id: string
  name: string
  contact_name?: string
  email?: string
  phone?: string
  address?: string
  tax_number?: string
  is_active: boolean
}

export type Supplier = Partner
export type Customer = Partner

// ── API Response Types ────────────────────────────────────────

export interface ApiResponse<T = unknown> {
  success: boolean
  message: string
  data?: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ApiError {
  success: false
  message: string
  error_code: string
  details?: Record<string, unknown>
}

// -- Inventory Types -------------------------------------------

export interface Warehouse {
  id: string
  company_id: string
  name: string
  code: string
  location?: string
  is_active: boolean
}

export interface StockItem {
  id: string
  company_id: string
  warehouse_id: string
  product_id: string
  quantity: string | number
  product?: Product
  warehouse?: Warehouse
}

export interface StockMovement {
  id: string
  company_id: string
  warehouse_id: string
  product_id: string
  movement_type: 'IN' | 'OUT' | 'TRANSFER'
  quantity: string | number
  reference?: string
  notes?: string
  created_at: string
  product?: Product
  warehouse?: Warehouse
}
