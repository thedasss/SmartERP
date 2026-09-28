import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar,
  AreaChart, Area
} from 'recharts';
import { reportsApi } from '../../services/reportsApi';
import type { SalesTrendData, InventoryValuationData, CashFlowData } from '../../services/reportsApi';
import { formatCurrency } from '../../utils/formatters';

export const ReportsPage: React.FC = () => {
  const [salesData, setSalesData] = useState<SalesTrendData[]>([]);
  const [invData, setInvData] = useState<InventoryValuationData[]>([]);
  const [cashData, setCashData] = useState<CashFlowData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [sales, inv, cash] = await Promise.all([
          reportsApi.getSalesTrend(),
          reportsApi.getInventoryValuation(),
          reportsApi.getCashFlow()
        ]);
        setSalesData(sales);
        setInvData(inv);
        setCashData(cash);
      } catch (err) {
        console.error('Failed to fetch report data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const customTooltip = (value: any) => [formatCurrency(Number(value)), ''];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
        <p className="text-gray-500 mt-1">Visualize your key business metrics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Sales Trend */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Sales Trend (Revenue over Time)</h2>
          {salesData.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-gray-400">No Sales Data Available</div>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={salesData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB"/>
                  <XAxis dataKey="date" tick={{fontSize: 12, fill: '#6B7280'}} axisLine={false} tickLine={false} />
                  <YAxis tickFormatter={(val) => `$${val}`} tick={{fontSize: 12, fill: '#6B7280'}} axisLine={false} tickLine={false}/>
                  <Tooltip formatter={customTooltip} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                  <Legend />
                  <Line type="monotone" dataKey="total_sales" name="Total Sales" stroke="#4F46E5" strokeWidth={3} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Inventory Valuation */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Inventory Valuation by Category</h2>
          {invData.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-gray-400">No Inventory Data Available</div>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={invData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB"/>
                  <XAxis dataKey="category_name" tick={{fontSize: 12, fill: '#6B7280'}} axisLine={false} tickLine={false} />
                  <YAxis tickFormatter={(val) => `$${val}`} tick={{fontSize: 12, fill: '#6B7280'}} axisLine={false} tickLine={false}/>
                  <Tooltip formatter={customTooltip} cursor={{fill: '#F3F4F6'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}/>
                  <Legend />
                  <Bar dataKey="total_value" name="Total Value" fill="#10B981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Cash Flow */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 lg:col-span-2">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Cash Flow (Money In vs Money Out)</h2>
          {cashData.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-gray-400">No Payment Data Available</div>
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={cashData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorIn" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorOut" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB"/>
                  <XAxis dataKey="date" tick={{fontSize: 12, fill: '#6B7280'}} axisLine={false} tickLine={false} />
                  <YAxis tickFormatter={(val) => `$${val}`} tick={{fontSize: 12, fill: '#6B7280'}} axisLine={false} tickLine={false}/>
                  <Tooltip formatter={customTooltip} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}/>
                  <Legend />
                  <Area type="monotone" dataKey="money_in" name="Money In (Received)" stroke="#10B981" fillOpacity={1} fill="url(#colorIn)" />
                  <Area type="monotone" dataKey="money_out" name="Money Out (Paid)" stroke="#EF4444" fillOpacity={1} fill="url(#colorOut)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
