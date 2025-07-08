import React, { useState, useEffect } from 'react';
import { FiCreditCard, FiCheck, FiX, FiArrowRight, FiDownload, FiCalendar } from 'react-icons/fi';

const BillingPage = () => {
  const [organization, setOrganization] = useState(null);
  const [billingHistory, setBillingHistory] = useState([]);
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBillingData();
    fetchSubscriptionPlans();
  }, []);

  const fetchBillingData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Get organization first
      const orgResponse = await fetch('http://127.0.0.1:8000/api/organizations/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const orgData = await orgResponse.json();
      
      if (orgData.results && orgData.results.length > 0) {
        const org = orgData.results[0];
        setOrganization(org);
        
        // Get billing data
        const billingResponse = await fetch(`http://127.0.0.1:8000/api/billing/${org.id}/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const billingData = await billingResponse.json();
        setBillingHistory(billingData.billing_history || []);
      }
    } catch (error) {
      console.error('Error fetching billing data:', error);
    }
  };

  const fetchSubscriptionPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/subscription-plans/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setSubscriptionPlans(data.results || []);
    } catch (error) {
      console.error('Error fetching subscription plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planName) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/billing/create-checkout-session/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          organization_id: organization.id,
          plan_name: planName
        })
      });
      
      const data = await response.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Billing & Subscription</h1>
          <p className="text-gray-600">Manage your subscription and billing information</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Current Plan */}
        {organization && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Current Plan</h2>
                <p className="text-3xl font-bold text-cyan-600 mt-2">
                  {organization.subscription_plan.display_name}
                </p>
                <p className="text-gray-600">
                  ${organization.subscription_plan.price_monthly}/month
                </p>
              </div>
              <div className="text-right">
                <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                  organization.subscription_status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {organization.subscription_status}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Subscription Plans */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Available Plans</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {subscriptionPlans.map((plan) => (
              <PlanCard 
                key={plan.name}
                plan={plan}
                currentPlan={organization?.subscription_plan.name}
                onUpgrade={handleUpgrade}
              />
            ))}
          </div>
        </div>

        {/* Billing History */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Billing History</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Period
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Invoice
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {billingHistory.length > 0 ? billingHistory.map((invoice) => (
                  <tr key={invoice.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(invoice.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${invoice.amount} {invoice.currency}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        invoice.status === 'paid' 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(invoice.billing_period_start).toLocaleDateString()} - {' '}
                      {new Date(invoice.billing_period_end).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button className="text-cyan-600 hover:text-cyan-800">
                        <FiDownload className="inline mr-1" />
                        Download
                      </button>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                      No billing history available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const PlanCard = ({ plan, currentPlan, onUpgrade }) => {
  const isCurrentPlan = plan.name === currentPlan;
  const isPopular = plan.name === 'professional';

  const features = [
    `${plan.max_datasets_per_month === 999999 ? 'Unlimited' : plan.max_datasets_per_month} datasets/month`,
    `${plan.max_dashboards === 999999 ? 'Unlimited' : plan.max_dashboards} dashboards`,
    `${plan.max_api_calls_per_month === 999999 ? 'Unlimited' : plan.max_api_calls_per_month.toLocaleString()} API calls/month`,
    `Up to ${plan.max_users_per_org} team members`,
  ];

  if (plan.has_advanced_analytics) features.push('Advanced Analytics');
  if (plan.has_custom_models) features.push('Custom ML Models');
  if (plan.has_api_access) features.push('API Access');
  if (plan.has_sso) features.push('SSO Integration');
  if (plan.has_white_label) features.push('White Label');

  return (
    <div className={`relative bg-white rounded-xl shadow-sm border-2 p-6 ${
      isCurrentPlan ? 'border-cyan-500' : 'border-gray-200'
    } ${isPopular ? 'ring-2 ring-cyan-500' : ''}`}>
      {isPopular && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <span className="bg-cyan-500 text-white px-3 py-1 rounded-full text-sm font-medium">
            Most Popular
          </span>
        </div>
      )}
      
      <div className="text-center mb-6">
        <h3 className="text-xl font-semibold text-gray-900">{plan.display_name}</h3>
        <div className="mt-2">
          <span className="text-3xl font-bold text-gray-900">${plan.price_monthly}</span>
          <span className="text-gray-600">/month</span>
        </div>
        {plan.price_yearly > 0 && (
          <p className="text-sm text-gray-500 mt-1">
            ${plan.price_yearly}/year (save 2 months)
          </p>
        )}
      </div>

      <ul className="space-y-3 mb-6">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center">
            <FiCheck className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />
            <span className="text-sm text-gray-600">{feature}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={() => onUpgrade(plan.name)}
        disabled={isCurrentPlan}
        className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
          isCurrentPlan
            ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
            : 'bg-cyan-500 text-white hover:bg-cyan-600'
        }`}
      >
        {isCurrentPlan ? 'Current Plan' : 'Upgrade'}
        {!isCurrentPlan && <FiArrowRight className="inline ml-2" />}
      </button>
    </div>
  );
};

export default BillingPage;
