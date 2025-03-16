import { useState, useEffect } from 'react';
import { FiDatabase, FiLink, FiPlus, FiRefreshCw, FiServer, FiSettings, FiTrash2 } from 'react-icons/fi';
import Sidebar from './Sidebar';
import Header from './Header';

const DataStreams = () => {
  const [streams, setStreams] = useState([]);
  const [newStream, setNewStream] = useState({
    name: '',
    type: 'api',
    url: '',
    refreshInterval: '60',
    credentials: { username: '', password: '' }
  });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [testResults] = useState({});

  // Simulated initial data (replace with Django API call)
  useEffect(() => {
    // Fetch existing streams from Django API
    const mockStreams = [
      {
        id: 1,
        name: 'Sales API',
        type: 'api',
        url: 'https://api.salesdata.com/v2',
        status: 'connected',
        lastUpdated: '2023-07-20T15:30:00Z',
        dataFormat: 'JSON'
      },
      {
        id: 2,
        name: 'Customer DB',
        type: 'database',
        url: 'postgres://customer-db/prod',
        status: 'disconnected',
        lastUpdated: '2023-07-19T10:15:00Z',
        dataFormat: 'SQL'
      }
    ];
    setStreams(mockStreams);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Add Django API POST request here
    const newStreamEntry = {
      ...newStream,
      id: streams.length + 1,
      status: 'connecting',
      lastUpdated: new Date().toISOString()
    };
    setStreams([...streams, newStreamEntry]);
    setNewStream({
      name: '',
      type: 'api',
      url: '',
      refreshInterval: '60',
      credentials: { username: '', password: '' }
    });
  };

  return (
    <div className="min-h-screen bg-white">
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Main Content */}
      <div className="md:ml-64 p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-semibold flex items-center">
            <FiDatabase className="mr-2 text-cyan-500" />
            Data Streams Management
          </h2>
          <button className="bg-cyan-500 text-white px-4 py-2 rounded-lg hover:bg-cyan-600 flex items-center">
            <FiPlus className="mr-2" />
            Add Stream
          </button>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Connection Form */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Configure New Data Stream</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Stream Name</label>
                <input
                  type="text"
                  required
                  className="w-full p-2 border rounded-lg"
                  value={newStream.name}
                  onChange={(e) => setNewStream({ ...newStream, name: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Connection Type</label>
                <select
                  className="w-full p-2 border rounded-lg"
                  value={newStream.type}
                  onChange={(e) => setNewStream({ ...newStream, type: e.target.value })}
                >
                  <option value="api">API Endpoint</option>
                  <option value="database">Database</option>
                  <option value="warehouse">Data Warehouse</option>
                  <option value="csv">CSV Upload</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {newStream.type === 'csv' ? 'File Upload' : 'Connection URL'}
                </label>
                <input
                  type={newStream.type === 'csv' ? 'file' : 'text'}
                  required
                  className="w-full p-2 border rounded-lg"
                  onChange={(e) => {
                    if (newStream.type === 'csv') {
                      // Handle file upload
                    } else {
                      setNewStream({ ...newStream, url: e.target.value });
                    }
                  }}
                />
              </div>

              {newStream.type !== 'csv' && (
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">Credentials</label>
                  <input
                    type="text"
                    placeholder="Username"
                    className="w-full p-2 border rounded-lg"
                    value={newStream.credentials.username}
                    onChange={(e) => setNewStream({
                      ...newStream,
                      credentials: { ...newStream.credentials, username: e.target.value }
                    })}
                  />
                  <input
                    type="password"
                    placeholder="Password"
                    className="w-full p-2 border rounded-lg"
                    value={newStream.credentials.password}
                    onChange={(e) => setNewStream({
                      ...newStream,
                      credentials: { ...newStream.credentials, password: e.target.value }
                    })}
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Refresh Interval (minutes)</label>
                <select
                  className="w-full p-2 border rounded-lg"
                  value={newStream.refreshInterval}
                  onChange={(e) => setNewStream({ ...newStream, refreshInterval: e.target.value })}
                >
                  <option value="15">15 Minutes</option>
                  <option value="30">30 Minutes</option>
                  <option value="60">1 Hour</option>
                  <option value="1440">Daily</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full bg-cyan-500 text-white py-2 rounded-lg hover:bg-cyan-600 flex items-center justify-center"
              >
                <FiLink className="mr-2" />
                Connect Stream
              </button>
            </form>
          </div>

          {/* Active Streams List */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4">Active Data Streams</h3>
            <div className="space-y-4">
              {streams.map((stream) => (
                <div key={stream.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        stream.status === 'connected' ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                      <h4 className="font-medium">{stream.name}</h4>
                      <span className="ml-2 text-sm text-gray-500">({stream.type})</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        // onClick={() => testConnection(stream.id)}
                        className="text-gray-500 hover:text-cyan-600"
                      >
                        <FiRefreshCw />
                      </button>
                      <button className="text-gray-500 hover:text-red-600">
                        <FiTrash2 />
                      </button>
                    </div>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">{stream.url}</div>
                  <div className="flex justify-between text-sm">
                    <div className="text-gray-500">
                      Last updated: {new Date(stream.lastUpdated).toLocaleString()}
                    </div>
                    <div className="flex items-center">
                      <FiServer className="mr-1 text-gray-400" />
                      <span className="text-gray-500">{stream.dataFormat}</span>
                    </div>
                  </div>
                  {testResults[stream.id] && (
                    <div className={`mt-2 p-2 rounded text-sm ${
                      testResults[stream.id].status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {testResults[stream.id].message}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Data Preview Section */}
        <div className="mt-8 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Stream Data Preview</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center mb-2">
                <FiDatabase className="mr-2 text-cyan-500" />
                <span className="font-medium">Sales Data Structure</span>
              </div>
              <pre className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                {JSON.stringify({
                  date: "2023-07-20",
                  amount: 2450.5,
                  product: "AI Software",
                  region: "North America"
                }, null, 2)}
              </pre>
            </div>
            <div className="p-4 border rounded-lg">
              <div className="flex items-center mb-2">
                <FiSettings className="mr-2 text-cyan-500" />
                <span className="font-medium">Connection Metrics</span>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Latency:</span>
                  <span className="text-green-600">142ms</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Data Volume:</span>
                  <span>24.5 MB</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Last Fetch:</span>
                  <span>15 seconds ago</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataStreams;