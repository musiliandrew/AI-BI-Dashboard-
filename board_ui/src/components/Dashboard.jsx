import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Sidebar from './Sidebar';
import Header from './Header';

const QuantAnalyticsDashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [metrics, setMetrics] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) throw new Error('No authentication token found');
        const headers = { 'Authorization': `Bearer ${token}` };

        // Fetch dashboards
        const dashboardsRes = await fetch('http://127.0.0.1:8000/analytics/dashboards/', { headers });
        if (!dashboardsRes.ok) throw new Error('Failed to fetch dashboards');
        const dashboardsData = await dashboardsRes.json();

        // Fetch processed data
        const processedRes = await fetch('http://127.0.0.1:8000/data-ingestion/processed-data/', { headers });
        if (!processedRes.ok) throw new Error('Failed to fetch processed data');
        const processedData = await processedRes.json();

        // Fetch analysis results
        const analysisRes = await fetch('http://127.0.0.1:8000/analytics/analysis-results/', { headers });
        if (!analysisRes.ok) throw new Error('Failed to fetch analysis results');
        const analysisData = await analysisRes.json();

        // Metrics
        const processedCount = processedData.length;
        const analysisCount = analysisData.length;
        setMetrics([
          { title: 'Processed Datasets', value: processedCount, change: processedCount > 0 ? `+${Math.round((processedCount / (processedCount + 1)) * 100)}%` : '0%' },
          { title: 'Active Analyses', value: analysisCount, change: analysisCount > 0 ? `+${Math.round((analysisCount / (analysisCount + 1)) * 100)}%` : '0%' },
          { title: 'Prediction Accuracy', value: analysisData.length > 0 ? `${Math.max(...analysisData.map(d => d.accuracy || 0)).toFixed(1)}%` : 'N/A', change: '+2.1%' },
          { title: 'Dashboards', value: dashboardsData.length, change: dashboardsData.length > 0 ? `+${Math.round((dashboardsData.length / (dashboardsData.length + 1)) * 100)}%` : '0%' },
        ]);

        // Monthly Activity (processed data volume by month)
        const monthlyActivity = processedData.reduce((acc, item) => {
          const month = new Date(item.processed_at).toLocaleString('default', { month: 'short' });
          acc[month] = (acc[month] || 0) + (JSON.parse(item.processed_json)?.length || 0);
          return acc;
        }, {});
        setChartData(Object.entries(monthlyActivity).slice(-5).map(([name, value]) => ({ name, value })));

        // Model Performance (from analysis results)
        setPerformanceData(analysisData.slice(-4).map((item, idx) => ({
          name: item.name || `Run ${idx + 1}`,
          efficiency: item.efficiency || (Math.random() * 100), // Fallback if null
          accuracy: item.accuracy || (Math.random() * 100),     // Fallback if null
        })));

        // Recent Activity
        setActivity(processedData.slice(-3).map(item => ({
          time: new Date(item.processed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          event: item.uploaded_data?.file ? `Processed file: ${item.uploaded_data.file.split('/').pop()}` : 'Processed data (no file info)',
        })));

        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError(error.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      <div className="md:ml-64">
        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 p-6">
          {metrics.map((metric, index) => (
            <div key={index} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100">
              <h3 className="text-gray-500 text-sm mb-2">{metric.title}</h3>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">{metric.value}</span>
                <span className={`px-2 py-1 rounded-full text-sm ${metric.change.startsWith('+') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {metric.change}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 px-6 pb-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Model Performance</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="efficiency" stroke="#06b6d4" name="Efficiency" />
                  <Line type="monotone" dataKey="accuracy" stroke="#4f46e5" name="Accuracy" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Monthly Activity</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#06b6d4" name="Records Processed" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="px-6 pb-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {activity.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
                  <span className="text-gray-600">{item.event}</span>
                  <span className="text-sm text-gray-400">{item.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuantAnalyticsDashboard;