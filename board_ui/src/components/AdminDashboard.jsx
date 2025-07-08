import React, { useState, useEffect } from 'react';
import { 
  FiUsers, FiDollarSign, FiActivity, FiTrendingUp, FiServer, 
  FiAlertTriangle, FiBarChart3, FiPieChart 
} from 'react-icons/fi';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar 
} from 'recharts';

const AdminDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [usageAnalytics, setUsageAnalytics] = useState(null);
  const [billingData, setBillingData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Fetch platform metrics
      const metricsResponse = await fetch('http://127.0.0.1:8000/api/admin/dashboard/', { headers });
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

      // Fetch usage analytics
      const usageResponse = await fetch('http://127.0.0.1:8000/api/admin/usage-analytics/', { headers });
      const usageData = await usageResponse.json();
      setUsageAnalytics(usageData);

      // Fetch billing data
      const billingResponse = await fetch('http://127.0.0.1:8000/api/admin/billing/', { headers });
      const billing = await billingResponse.json();
      setBillingData(billing);

    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  const COLORS = ['#06b6d4', '#4f46e5', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600">Platform-wide analytics and management</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Organizations"
            value={metrics?.metrics.total_organizations || 0}
            change={`+${metrics?.metrics.new_organizations || 0} this month`}
            icon={FiUsers}
            color="cyan"
          />
          <MetricCard
            title="Total Users"
            value={metrics?.metrics.total_users || 0}
            change={`+${metrics?.metrics.new_users || 0} this month`}
            icon={FiUsers}
            color="indigo"
          />
          <MetricCard
            title="Monthly Revenue"
            value={`$${(metrics?.metrics.monthly_revenue || 0).toLocaleString()}`}
            change="+12.5% vs last month"
            icon={FiDollarSign}
            color="green"
          />
          <MetricCard
            title="Active Subscriptions"
            value={metrics?.metrics.active_subscriptions || 0}
            change="98.5% retention rate"
            icon={FiActivity}
            color="yellow"
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Trends */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Revenue Trends</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={billingData?.revenue_by_month || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value}`, 'Revenue']} />
                  <Line type="monotone" dataKey="total_revenue" stroke="#06b6d4" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Subscription Distribution */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Subscription Plans</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={metrics?.subscription_breakdown || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ subscription_plan__display_name, percent }) => 
                      `${subscription_plan__display_name} ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {(metrics?.subscription_breakdown || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Usage Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* API Usage Trends */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">API Usage Trends</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={usageAnalytics?.usage_trends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#4f46e5" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Endpoints */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Top API Endpoints</h3>
            <div className="space-y-3">
              {(usageAnalytics?.top_endpoints || []).slice(0, 8).map((endpoint, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 truncate">
                    {endpoint.metadata__endpoint || 'Unknown'}
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    {endpoint.count.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Organizations */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Top Organizations by Usage</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Organization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Plan
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    API Calls
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Datasets
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(metrics?.top_organizations || []).slice(0, 10).map((org) => (
                  <tr key={org.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{org.name}</div>
                      <div className="text-sm text-gray-500">{org.slug}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {org.subscription_plan?.display_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {org.current_month_api_calls?.toLocaleString() || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {org.current_month_datasets || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        org.subscription_status === 'active' 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {org.subscription_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, change, icon: Icon, color }) => {
  const getColorClasses = (color) => {
    const colors = {
      cyan: 'bg-cyan-50 text-cyan-600 border-cyan-200',
      indigo: 'bg-indigo-50 text-indigo-600 border-indigo-200',
      green: 'bg-green-50 text-green-600 border-green-200',
      yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    };
    return colors[color] || colors.cyan;
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${getColorClasses(color)}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      <h3 className="text-sm font-medium text-gray-500 mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-sm text-gray-600">{change}</p>
    </div>
  );
};

export default AdminDashboard;
