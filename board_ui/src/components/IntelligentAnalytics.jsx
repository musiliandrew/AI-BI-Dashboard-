import React, { useState, useEffect } from 'react';
import { 
  FiUpload, FiZap, FiBrain, FiTrendingUp, FiUsers, FiDollarSign, 
  FiBarChart3, FiAlertCircle, FiCheckCircle, FiClock, FiEye 
} from 'react-icons/fi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterPlot, Scatter } from 'recharts';

const IntelligentAnalytics = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [processedDataId, setProcessedDataId] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState('upload'); // upload, analyzing, recommendations, results

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadedFile(file);
    setLoading(true);
    setStage('analyzing');

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      // Upload file
      const uploadResponse = await fetch('http://127.0.0.1:8000/api/data-ingestion/upload/', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (!uploadResponse.ok) throw new Error('Upload failed');
      const uploadData = await uploadResponse.json();

      // Wait for processing
      await waitForProcessing(uploadData.uploaded_data_id);

      // Get intelligent recommendations
      const analyzeResponse = await fetch('http://127.0.0.1:8000/api/analytics/intelligent-analyze/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ processed_data_id: processedDataId })
      });

      if (!analyzeResponse.ok) throw new Error('Analysis failed');
      const analysisData = await analyzeResponse.json();

      // Poll for results
      await pollForResults(analysisData.task_id);

    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const waitForProcessing = async (uploadedDataId) => {
    const token = localStorage.getItem('token');
    let processed = false;
    
    while (!processed) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const response = await fetch('http://127.0.0.1:8000/api/data-ingestion/processed-data/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const data = await response.json();
      const matchingRecord = data.find(p => p.uploaded_data.id === uploadedDataId);
      
      if (matchingRecord) {
        setProcessedDataId(matchingRecord.id);
        processed = true;
      }
    }
  };

  const pollForResults = async (taskId) => {
    const token = localStorage.getItem('token');
    let completed = false;
    
    while (!completed) {
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const response = await fetch('http://127.0.0.1:8000/api/analytics/analysis-results/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const results = await response.json();
      const latestResult = results[results.length - 1];
      
      if (latestResult && latestResult.recommendations) {
        const recs = JSON.parse(latestResult.recommendations);
        setRecommendations(recs);
        setStage('recommendations');
        completed = true;
      }
    }
  };

  const executeAnalysis = async (analysisType) => {
    setSelectedAnalysis(analysisType);
    setLoading(true);
    setStage('results');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/analytics/intelligent-analyze/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          processed_data_id: processedDataId,
          selected_analysis: analysisType
        })
      });

      const data = await response.json();
      await pollForAnalysisResults(data.task_id);

    } catch (error) {
      console.error('Error executing analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const pollForAnalysisResults = async (taskId) => {
    const token = localStorage.getItem('token');
    let completed = false;
    
    while (!completed) {
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const response = await fetch('http://127.0.0.1:8000/api/analytics/analysis-results/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const results = await response.json();
      const latestResult = results[results.length - 1];
      
      if (latestResult && latestResult.factors) {
        const factors = JSON.parse(latestResult.factors);
        setAnalysisResults(factors);
        completed = true;
      }
    }
  };

  const getAnalysisIcon = (type) => {
    const icons = {
      'sales_forecasting': FiTrendingUp,
      'credit_risk': FiDollarSign,
      'customer_segmentation': FiUsers,
      'correlation_analysis': FiBarChart3,
      'anomaly_detection': FiAlertCircle,
      'descriptive_analytics': FiEye
    };
    return icons[type] || FiBrain;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center space-x-3">
            <FiBrain className="h-8 w-8 text-cyan-500" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Intelligent Analytics</h1>
              <p className="text-gray-600">AI-powered data analysis that understands your data automatically</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Upload Stage */}
        {stage === 'upload' && (
          <div className="text-center">
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 hover:border-cyan-400 transition-colors">
              <FiUpload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Your Dataset</h3>
              <p className="text-gray-600 mb-6">
                Our AI will automatically analyze your data and suggest the best analytics approach
              </p>
              <input
                type="file"
                accept=".csv,.xlsx,.json"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="inline-flex items-center px-6 py-3 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 cursor-pointer transition-colors"
              >
                <FiUpload className="mr-2" />
                Choose File
              </label>
              <p className="text-sm text-gray-500 mt-4">Supports CSV, Excel, and JSON files</p>
            </div>
          </div>
        )}

        {/* Analyzing Stage */}
        {stage === 'analyzing' && (
          <div className="text-center">
            <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-100">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-500 mx-auto mb-6"></div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Analyzing Your Data</h3>
              <p className="text-gray-600">
                Our AI is understanding your dataset structure and identifying the best analysis approaches...
              </p>
              <div className="mt-6 space-y-2">
                <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                  <FiCheckCircle className="text-green-500" />
                  <span>Data uploaded and processed</span>
                </div>
                <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                  <FiClock className="text-yellow-500" />
                  <span>Analyzing data structure and patterns</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recommendations Stage */}
        {stage === 'recommendations' && recommendations.length > 0 && (
          <div>
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Recommendations</h2>
              <p className="text-gray-600">
                Based on your data analysis, here are the recommended analytics approaches:
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((rec, index) => {
                const Icon = getAnalysisIcon(rec.analysis_type);
                return (
                  <div key={index} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-cyan-50 rounded-lg">
                          <Icon className="h-6 w-6 text-cyan-600" />
                        </div>
                        <h3 className="font-semibold text-gray-900">
                          {rec.analysis_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </h3>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(rec.confidence)}`}>
                        {(rec.confidence * 100).toFixed(0)}%
                      </span>
                    </div>

                    <p className="text-gray-600 text-sm mb-4">{rec.explanation}</p>

                    {rec.missing_columns.length > 0 && (
                      <div className="mb-4">
                        <p className="text-sm font-medium text-red-600 mb-1">Missing:</p>
                        <ul className="text-xs text-red-500 space-y-1">
                          {rec.missing_columns.map((col, i) => (
                            <li key={i}>• {col}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {rec.alternative_approaches.length > 0 && (
                      <div className="mb-4">
                        <p className="text-sm font-medium text-gray-600 mb-1">Alternatives:</p>
                        <ul className="text-xs text-gray-500 space-y-1">
                          {rec.alternative_approaches.map((alt, i) => (
                            <li key={i}>• {alt}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <button
                      onClick={() => executeAnalysis(rec.analysis_type)}
                      disabled={rec.confidence < 0.3}
                      className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                        rec.confidence >= 0.3
                          ? 'bg-cyan-500 text-white hover:bg-cyan-600'
                          : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {rec.confidence >= 0.3 ? 'Run Analysis' : 'Low Confidence'}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Results Stage */}
        {stage === 'results' && (
          <div>
            {loading ? (
              <div className="text-center">
                <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-100">
                  <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-500 mx-auto mb-6"></div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Running Analysis</h3>
                  <p className="text-gray-600">
                    Executing {selectedAnalysis?.replace('_', ' ')} analysis...
                  </p>
                </div>
              </div>
            ) : analysisResults ? (
              <div>
                <div className="mb-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Results</h2>
                  <p className="text-gray-600">
                    {selectedAnalysis?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Analysis Complete
                  </p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(analysisResults, null, 2)}
                  </pre>
                </div>

                <div className="mt-6 text-center">
                  <button
                    onClick={() => {
                      setStage('recommendations');
                      setAnalysisResults(null);
                      setSelectedAnalysis(null);
                    }}
                    className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Try Another Analysis
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};

export default IntelligentAnalytics;
