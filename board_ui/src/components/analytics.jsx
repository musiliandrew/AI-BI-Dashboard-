import { useState, useEffect } from 'react';
import { FiBarChart2, FiUpload } from 'react-icons/fi';
import Sidebar from './Sidebar';
import Header from './Header';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from 'recharts';

const Analytics = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
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
        // Use processed_json from processed_data
        setColumns(data.length > 0 ? Object.keys(JSON.parse(data[data.length - 1].processed_data.processed_json)[0]) : []);
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
        body: JSON.stringify({ processed_data_id: latestResult.processed_data.id, column_mappings: userMappings[selectedAnalysis] }),
      });
      if (!analyzeRes.ok) throw new Error('Analysis failed');

      await fetchResults(userMappings[selectedAnalysis]);
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

  return (
    <div className="min-h-screen bg-white">
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

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
            >
              <FiUpload className="mr-2" /> {loading ? 'Processing...' : 'Analyze File'}
            </button>
          </form>
        </div>

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
              disabled={loading || !selectedAnalysis}
            >
              {loading ? 'Running Analysis...' : 'Run Analysis with Mappings'}
            </button>
          </div>
        )}

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
          </div>
        )}

        {error && <p className="text-red-500 mt-4">Error: {error}</p>}
      </div>
    </div>
  );
};

export default Analytics;