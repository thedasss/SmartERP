/**
 * App root — React Router configuration.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

import ProtectedRoute from '@/components/ProtectedRoute'
import DashboardLayout from '@/layouts/DashboardLayout'
import LoginPage from '@/features/auth/LoginPage'
import DashboardPage from '@/features/dashboard/DashboardPage'
import ProductsPage from '@/features/master-data/ProductsPage'
import SuppliersPage from '@/features/master-data/SuppliersPage'
import CustomersPage from '@/features/master-data/CustomersPage'
import WarehousesPage from '@/features/inventory/WarehousesPage'
import StockPage from '@/features/inventory/StockPage'
import { PurchaseOrdersPage } from '@/pages/procurement/PurchaseOrdersPage'
import { SalesOrdersPage } from '@/pages/sales/SalesOrdersPage'
import { InvoicesPage } from '@/pages/finance/InvoicesPage'
import { ReportsPage } from '@/pages/reports/ReportsPage'
import { DocumentsPage } from '@/pages/documents/DocumentsPage'
import { AIPage } from '@/pages/ai/AIPage'
import { UsersPage } from '@/pages/users/UsersPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
})

// Placeholder pages for routes added in future phases
const Placeholder = ({ name }: { name: string }) => (
  <div className="flex items-center justify-center h-64">
    <div className="text-center">
      <h2 className="text-xl font-semibold text-dark-100">{name}</h2>
      <p className="text-dark-400 mt-2 text-sm">This module will be implemented in the next phase.</p>
    </div>
  </div>
)

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="procurement" element={<PurchaseOrdersPage />} />
            <Route path="sales" element={<SalesOrdersPage />} />
            <Route path="products" element={<ProductsPage />} />
            <Route path="suppliers" element={<SuppliersPage />} />
            <Route path="customers" element={<CustomersPage />} />
            <Route path="invoices" element={<InvoicesPage />} />
            <Route path="warehouses" element={<WarehousesPage />} />
            <Route path="stock" element={<StockPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="ai" element={<AIPage />} />
            <Route path="users" element={<UsersPage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>

      <Toaster
        position="top-right"
        toastOptions={{
          className: '',
          style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid #334155',
            borderRadius: '12px',
          },
          success: { iconTheme: { primary: '#6366f1', secondary: '#fff' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#fff' } },
        }}
      />
    </QueryClientProvider>
  )
}

export default App
