<<<<<<< Updated upstream
import { useState } from 'react';
import { FiUploadCloud } from 'react-icons/fi';
import { LineChart, Line, BarChart, Bar, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
=======
import { useState, useEffect } from 'react';
import { FiBarChart2, FiUpload } from 'react-icons/fi';
>>>>>>> Stashed changes
import Sidebar from './Sidebar';
import Header from './Header';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from 'recharts';

const Analytics = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
<<<<<<< Updated upstream

  const salesData = [
    { month: 'Jan', actual: 65, predicted: 70 },
    { month: 'Feb', actual: 80, predicted: 78 },
    { month: 'Mar', actual: 75, predicted: 82 },
    { month: 'Apr', actual: 90, predicted: 88 },
    { month: 'May', actual: 85, predicted: 91 },
  ];

  const riskData = [
    { customer: 'C001', score: 42, risk: 'High' },
    { customer: 'C002', score: 78, risk: 'Low' },
    { customer: 'C003', score: 65, risk: 'Medium' },
    { customer: 'C004', score: 88, risk: 'Low' },
    { customer: 'C005', score: 35, risk: 'High' },
  ];

  const clusterData = [
    { x: 25, y: 50, cluster: 'Group A' },
    { x: 45, y: 75, cluster: 'Group B' },
    { x: 15, y: 30, cluster: 'Group A' },
    { x: 60, y: 85, cluster: 'Group C' },
    { x: 70, y: 40, cluster: 'Group D' },
  ];

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
      console.log('Uploaded file:', file.name);
    }
  };

=======
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [results, setResults] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [suggestedMappings, setSuggestedMappings] = useState(null);
  const [userMappings, setUserMappings] = useState({});
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);

  const fetchResults = async (mappings = null) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No authentication token found');
      const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

      const res = await fetch('http://127.0.0.1:8000/analytics/analysis-results/', { headers });
      if (!res.ok) throw new Error('Failed to fetch results');
      const data = await res.json();
      const latestResult = data.length > 0 ? JSON.parse(data[data.length - 1].results) : null;
      
      if (latestResult?.recommendations && !mappings) {
        setRecommendations(latestResult.recommendations);
        setSuggestedMappings({
          credit_risk: latestResult.recommendations.credit_risk.suggested_mappings,
          segmentation: latestResult.recommendations.segmentation.suggested_mappings,
          sales_forecast: latestResult.recommendations.sales_forecast.suggested_mappings
        });
        setColumns(data.length > 0 ? Object.keys(JSON.parse(data[data.length - 1].processed_data.processed_content)[0]) : []);
      } else {
        setResults(latestResult?.analysis_results || null);
        setRecommendations(null);
        setSuggestedMappings(null);
      }
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
  
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', 'Analytics Upload');
  
      const uploadRes = await fetch('http://127.0.0.1:8000/data-ingestion/upload/', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });
      if (!uploadRes.ok) throw new Error('Upload failed');
      const uploadData = await uploadRes.json();
      console.log('Upload Response:', uploadData);
  
      let processedDataId = null;
      let attempts = 0;
      const maxAttempts = 60;
      const pollInterval = setInterval(async () => {
        attempts += 1;
        const processedRes = await fetch('http://127.0.0.1:8000/data-ingestion/processed-data/', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!processedRes.ok) {
          clearInterval(pollInterval);
          throw new Error('Failed to fetch processed data');
        }
        const processedData = await processedRes.json();
        console.log('Processed Data:', JSON.stringify(processedData, null, 2));
        console.log('Looking for uploaded_data_id:', uploadData.uploaded_data_id);
  
        // Fix: Compare p.uploaded_data.id (number) with uploadData.uploaded_data_id (number)
        const matchingRecord = processedData.find(p => p.uploaded_data.id === uploadData.uploaded_data_id);
        if (matchingRecord) {
          processedDataId = matchingRecord.id;
          console.log('Found ProcessedData ID:', processedDataId);
          clearInterval(pollInterval);
  
          const analyzeRes = await fetch('http://127.0.0.1:8000/analytics/analyze/', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ processed_data_id: processedDataId }),
          });
          if (!analyzeRes.ok) throw new Error('Analysis failed: ' + (await analyzeRes.text()));
  
          await fetchResults();
          setLoading(false);
        } else if (attempts >= maxAttempts) {
          clearInterval(pollInterval);
          throw new Error('Timeout: Processed data not found for uploaded_data_id ' + uploadData.uploaded_data_id);
        }
      }, 2000);
    } catch (err) {
      console.error('Error processing file:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const handleMappingSubmit = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const latestResult = await fetch('http://127.0.0.1:8000/analytics/analysis-results/', {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(res => res.json()).then(data => data[data.length - 1]);
      
      const analyzeRes = await fetch('http://127.0.0.1:8000/analytics/analyze/', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ processed_data_id: latestResult.processed_data.id, column_mappings: userMappings }),
      });
      if (!analyzeRes.ok) throw new Error('Analysis failed');

      await fetchResults(userMappings);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const updateMapping = (analysis, expectedVar, selectedCol) => {
    setUserMappings(prev => ({
      ...prev,
      [analysis]: { ...(prev[analysis] || {}), [expectedVar]: selectedCol }
    }));
  };

  const forecastData = results?.sales_forecast?.predictions ? results.sales_forecast.dates.map((date, i) => ({
    date: new Date(date).toLocaleDateString(),
    sales: results.sales_forecast.predictions[i],
  })) : [];

  const clusterData = results?.segmentation?.labels ? results.segmentation.labels.map((label, i) => ({
    name: `Customer ${i}`,
    cluster: label,
  })) : [];

  const riskData = results?.credit_risk?.risk_scores ? results.credit_risk.risk_scores.map((score, i) => ({
    name: `Borrower ${i}`,
    risk: score,
  })) : [];

>>>>>>> Stashed changes
  return (
    <div className="min-h-screen bg-white">
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

<<<<<<< Updated upstream
      {/* Main Content */}
      <div className="md:ml-64">
        <header className="bg-white shadow-sm">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-semibold">AI Analytics Engine</h2>
            </div>
            <div className="flex items-center space-x-4">
              <label className="flex items-center px-4 py-2 bg-cyan-100 text-cyan-800 rounded-lg cursor-pointer hover:bg-cyan-200">
                <FiUploadCloud className="mr-2" />
                {uploadedFile ? uploadedFile.name : 'Upload Dataset'}
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileUpload}
                  accept=".csv,.xlsx,.json"
                />
              </label>
              {uploadedFile && (
                <div className="text-sm text-gray-500">
                  ({Math.round(uploadedFile.size / 1024)} KB)
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Model Selection */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-6 border-b">
          {[
            { id: 'sales-forecast', label: 'Sales Forecast' },
            { id: 'risk-detection', label: 'Credit Risk' },
            { id: 'customer-clusters', label: 'Customer Clusters' },
            { id: 'product-analysis', label: 'Product Analysis' },
            { id: 'factor-analysis', label: 'Factor Analysis' },
          ].map((model) => (
            <button
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`p-3 text-sm rounded-lg ${
                selectedModel === model.id
                  ? 'bg-black text-white'
                  : 'bg-gray-50 hover:bg-gray-100'
              }`}
=======
      <div className="md:ml-64 p-6">
        <h2 className="text-2xl font-semibold mb-6 flex items-center">
          <FiBarChart2 className="mr-2 text-cyan-500" /> Analytics
        </h2>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
          <h3 className="text-lg font-semibold mb-4">Upload Data for Analysis</h3>
          <form onSubmit={handleFileUpload} className="space-y-4">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
              accept=".csv,.json"
              className="w-full p-2 border rounded-lg"
            />
            <button
              type="submit"
              className="bg-cyan-500 text-white px-4 py-2 rounded-lg hover:bg-cyan-600 flex items-center"
              disabled={loading}
>>>>>>> Stashed changes
            >
              <FiUpload className="mr-2" /> {loading ? 'Processing...' : 'Analyze File'}
            </button>
          </form>
        </div>

<<<<<<< Updated upstream
        {/* Analytics Dashboard */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
          {/* Main Chart */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">
              {selectedModel.replace(/-/g, ' ').toUpperCase()}
            </h3>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                {selectedModel === 'sales-forecast' ? (
                  <LineChart data={salesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="actual"
                      stroke="#06b6d4"
                      name="Actual Sales"
                    />
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      stroke="#4f46e5"
                      name="Predicted Sales"
                      strokeDasharray="5 5"
                    />
                  </LineChart>
                ) : selectedModel === 'risk-detection' ? (
                  <BarChart data={riskData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="customer" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="score" fill="#06b6d4" />
                  </BarChart>
                ) : (
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid />
                    <XAxis type="number" dataKey="x" name="X Value" />
                    <YAxis type="number" dataKey="y" name="Y Value" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter
                      name="Clusters"
                      data={clusterData}
                      fill="#06b6d4"
                    />
                  </ScatterChart>
                )}
              </ResponsiveContainer>
            </div>
          </div>

          {/* Insights Panel */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold mb-4">Key Insights</h3>
              <div className="space-y-3">
                <div className="p-3 bg-cyan-50 rounded-lg">
                  <h4 className="text-sm font-medium text-cyan-800">
                    Top Predictive Factors
                  </h4>
                  <ul className="mt-2 text-sm text-gray-600">
                    <li>• Marketing spend (35% impact)</li>
                    <li>• Seasonal trends (28% impact)</li>
                    <li>• Economic indicators (22% impact)</li>
                  </ul>
                </div>
                <div className="p-3 bg-purple-50 rounded-lg">
                  <h4 className="text-sm font-medium text-purple-800">
                    Model Performance
                  </h4>
                  <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500">Accuracy</div>
                      <div className="font-semibold">94.2%</div>
                    </div>
                    <div>
                      <div className="text-gray-500">Processing Time</div>
                      <div className="font-semibold">2.4s</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold mb-4">AI Recommendations</h3>
              <div className="space-y-3">
                <div className="flex items-start">
                  <span className="shrink-0 mt-1 w-2 h-2 bg-cyan-400 rounded-full mr-3"></span>
                  <div className="text-sm">
                    Consider increasing marketing budget in Q3 based on predicted
                    seasonal uplift
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="shrink-0 mt-1 w-2 h-2 bg-cyan-400 rounded-full mr-3"></span>
                  <div className="text-sm">
                    High-risk customers detected: Recommend additional credit
                    checks for 15 accounts
                  </div>
                </div>
              </div>
            </div>
=======
        {suggestedMappings && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
            <h3 className="text-lg font-semibold mb-4">Confirm Column Mappings</h3>
            {Object.entries(recommendations).map(([analysis, { possible, suggested_mappings }]) => (
              possible && (
                <div key={analysis} className="mb-4">
                  <h4 className="font-medium">{analysis.replace('_', ' ').toUpperCase()}</h4>
                  {Object.entries(suggested_mappings).map(([expectedVar, suggestedCol]) => (
                    <div key={expectedVar} className="flex items-center space-x-2 mt-2">
                      <label className="text-sm text-gray-700">{expectedVar}:</label>
                      <select
                        value={userMappings[analysis]?.[expectedVar] || suggestedCol}
                        onChange={(e) => updateMapping(analysis, expectedVar, e.target.value)}
                        className="p-2 border rounded-lg"
                      >
                        {columns.map(col => (
                          <option key={col} value={col}>{col}</option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              )
            ))}
            <button
              onClick={handleMappingSubmit}
              className="bg-cyan-500 text-white px-4 py-2 rounded-lg hover:bg-cyan-600 mt-4"
              disabled={loading}
            >
              {loading ? 'Running Analysis...' : 'Run Analysis with Mappings'}
            </button>
>>>>>>> Stashed changes
          </div>
        )}

<<<<<<< Updated upstream
        {/* Data Summary */}
        <div className="px-6 pb-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Dataset Overview</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { label: 'Total Records', value: '24,532' },
                { label: 'Variables', value: '42' },
                { label: 'Time Range', value: 'Jan 2020 - Present' },
                { label: 'Data Quality', value: '98.4%' },
              ].map((metric, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold mb-1">{metric.value}</div>
                  <div className="text-sm text-gray-500">{metric.label}</div>
                </div>
              ))}
            </div>
=======
        {results && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Analysis Results</h3>
            <select
              value={selectedAnalysis || ''}
              onChange={(e) => setSelectedAnalysis(e.target.value)}
              className="mb-4 p-2 border rounded-lg"
            >
              <option value="">Select Analysis</option>
              {results.credit_risk && <option value="credit_risk">Credit Risk Analysis</option>}
              {results.segmentation && <option value="segmentation">Customer Segmentation</option>}
              {results.sales_forecast && <option value="sales_forecast">Sales Forecasting</option>}
            </select>

            {selectedAnalysis === 'sales_forecast' && forecastData.length > 0 && (
              <>
                <LineChart width={600} height={300} data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="sales" stroke="#00bcd4" />
                </LineChart>
                <p className="mt-2 text-gray-600">{results.sales_forecast.recommendation}</p>
              </>
            )}
            {selectedAnalysis === 'segmentation' && clusterData.length > 0 && (
              <>
                <BarChart width={600} height={300} data={clusterData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="cluster" fill="#00bcd4" />
                </BarChart>
                <p className="mt-2 text-gray-600">{results.segmentation.recommendation}</p>
              </>
            )}
            {selectedAnalysis === 'credit_risk' && riskData.length > 0 && (
              <>
                <BarChart width={600} height={300} data={riskData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="risk" fill="#00bcd4" />
                </BarChart>
                <p className="mt-2 text-gray-600">{results.credit_risk.recommendation}</p>
              </>
            )}
>>>>>>> Stashed changes
          </div>
        )}

        {error && <p className="text-red-500 mt-4">Error: {error}</p>}
      </div>
    </div>
  );
};

export default Analytics;