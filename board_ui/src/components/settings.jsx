import { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
// FiUploadCloud

const SettingsPage = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [formData, setFormData] = useState({
      apiKey: '',
      dataRetention: '30',
      notificationEmail: '',
      modelRefreshRate: 'daily',
    });
    const [isSaving, setIsSaving] = useState(false);
  
    const handleInputChange = (e) => {
      const { name, value } = e.target;
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      setIsSaving(true);
      
      try {
        const response = await fetch('/api/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });
        
        if (response.ok) {
          alert('Settings saved successfully!');
        }
      } catch (error) {
        console.error('Error saving settings:', error);
        alert('Failed to save settings');
      }
      setIsSaving(false);
    };
  
    return (
      <div className="min-h-screen bg-white">
        <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
  
        <div className="md:ml-64">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-6">Settings</h2>
  
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">API Configuration</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        API Key
                      </label>
                      <input
                        type="text"
                        name="apiKey"
                        value={formData.apiKey}
                        onChange={handleInputChange}
                        className="w-full p-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                        placeholder="Enter your API key"
                      />
                    </div>
                  </div>
                </div>
  
                <div>
                  <h3 className="text-lg font-semibold mb-4">Data Settings</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Data Retention Period (days)
                      </label>
                      <select
                        name="dataRetention"
                        value={formData.dataRetention}
                        onChange={handleInputChange}
                        className="w-full p-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                      >
                        <option value="30">30 Days</option>
                        <option value="60">60 Days</option>
                        <option value="90">90 Days</option>
                        <option value="365">1 Year</option>
                      </select>
                    </div>
                  </div>
                </div>
  
                <div>
                  <h3 className="text-lg font-semibold mb-4">Notifications</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Notification Email
                      </label>
                      <input
                        type="email"
                        name="notificationEmail"
                        value={formData.notificationEmail}
                        onChange={handleInputChange}
                        className="w-full p-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                        placeholder="Enter email for notifications"
                      />
                    </div>
                  </div>
                </div>
  
                <div>
                  <h3 className="text-lg font-semibold mb-4">Model Settings</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Model Refresh Rate
                      </label>
                      <select
                        name="modelRefreshRate"
                        value={formData.modelRefreshRate}
                        onChange={handleInputChange}
                        className="w-full p-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                      >
                        <option value="hourly">Hourly</option>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                      </select>
                    </div>
                  </div>
                </div>
  
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={isSaving}
                    className={`px-6 py-2 rounded-lg text-white ${
                      isSaving ? 'bg-gray-400' : 'bg-cyan-600 hover:bg-cyan-700'
                    }`}
                  >
                    {isSaving ? 'Saving...' : 'Save Settings'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  export default SettingsPage;