import React, { useState, useEffect } from 'react';
import { 
  FiUsers, FiDatabase, FiActivity, FiCreditCard, FiSettings, 
  FiBarChart3, FiTrendingUp, FiAlertCircle 
} from 'react-icons/fi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const OrganizationDashboard = () => {
  const [organization, setOrganization] = useState(null);
  const [usageData, setUsageData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrganizationData();
  }, []);

  const fetchOrganizationData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch organization info
      const orgResponse = await fetch('http://127.0.0.1:8000/api/organizations/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const orgData = await orgResponse.json();
      
      if (orgData.results && orgData.results.length > 0) {
        const org = orgData.results[0];
        setOrganization(org);
        
        // Fetch usage analytics
        const usageResponse = await fetch(`http://127.0.0.1:8000/api/organizations/${org.id}/usage_analytics/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const usage = await usageResponse.json();
        setUsageData(usage);
      }
    } catch (error) {
      console.error('Error fetching organization data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading organization data...</p>
        </div>
      </div>
    );
  }

  if (!organization) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <FiAlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Organization Found</h2>
          <p className="text-gray-600">Please create an organization to continue.</p>
        </div>
      </div>
    );
  }

  const usagePercentages = organization.usage_percentage || {};
  const currentLimits = usageData?.current_limits || {};

  const COLORS = ['#06b6d4', '#4f46e5', '#10b981', '#f59e0b'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{organization.name}</h1>
              <p className="text-sm text-gray-600">
                {organization.subscription_plan.display_name} Plan • {organization.subscription_status}
              </p>
            </div>
            <div className="flex space-x-3">
              <button className="px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-colors">
                <FiSettings className="inline mr-2" />
                Settings
              </button>
              <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                <FiCreditCard className="inline mr-2" />
                Billing
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Usage Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <UsageCard
            title="Datasets"
            used={currentLimits.datasets?.used || 0}
            limit={currentLimits.datasets?.limit || 0}
            percentage={usagePercentages.datasets || 0}
            icon={FiDatabase}
            color="cyan"
          />
          <UsageCard
            title="API Calls"
            used={currentLimits.api_calls?.used || 0}
            limit={currentLimits.api_calls?.limit || 0}
            percentage={usagePercentages.api_calls || 0}
            icon={FiActivity}
            color="indigo"
          />
          <UsageCard
            title="Team Members"
            used={currentLimits.users?.used || 0}
            limit={currentLimits.users?.limit || 0}
            percentage={usagePercentages.users || 0}
            icon={FiUsers}
            color="green"
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Usage Trends */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Usage Trends (30 Days)</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={usageData?.daily_usage || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#06b6d4" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Usage Breakdown */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Usage Breakdown</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={usageData?.usage_summary || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {(usageData?.usage_summary || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Plan Features */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Plan Features</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <FeatureItem 
              name="Advanced Analytics" 
              enabled={organization.subscription_plan.has_advanced_analytics} 
            />
            <FeatureItem 
              name="Custom Models" 
              enabled={organization.subscription_plan.has_custom_models} 
            />
            <FeatureItem 
              name="API Access" 
              enabled={organization.subscription_plan.has_api_access} 
            />
            <FeatureItem 
              name="SSO Integration" 
              enabled={organization.subscription_plan.has_sso} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const UsageCard = ({ title, used, limit, percentage, icon: Icon, color }) => {
  const getColorClasses = (color) => {
    const colors = {
      cyan: 'bg-cyan-50 text-cyan-600 border-cyan-200',
      indigo: 'bg-indigo-50 text-indigo-600 border-indigo-200',
      green: 'bg-green-50 text-green-600 border-green-200',
    };
    return colors[color] || colors.cyan;
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${getColorClasses(color)}`}>
          <Icon className="h-6 w-6" />
        </div>
        <span className="text-sm text-gray-500">{percentage.toFixed(1)}%</span>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600 mb-3">
        {used.toLocaleString()} / {limit.toLocaleString()}
      </p>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(percentage)}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        ></div>
      </div>
    </div>
  );
};

const FeatureItem = ({ name, enabled }) => (
  <div className="flex items-center space-x-2">
    <div className={`w-3 h-3 rounded-full ${enabled ? 'bg-green-500' : 'bg-gray-300'}`}></div>
    <span className={`text-sm ${enabled ? 'text-gray-900' : 'text-gray-500'}`}>{name}</span>
  </div>
);

export default OrganizationDashboard;
