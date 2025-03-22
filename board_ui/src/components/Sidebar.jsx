import { FiActivity, FiBarChart, FiDatabase, FiSettings } from 'react-icons/fi';
import { useNavigate, useLocation } from 'react-router-dom';
import PropTypes from 'prop-types';
import logo from '../assets/logo.png';

const Sidebar = ({ sidebarOpen, setSidebarOpen }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { id: 'dashboard', icon: <FiActivity />, label: 'Dashboard', path: '/dashboard' },
    { id: 'analytics', icon: <FiBarChart />, label: 'Analytics', path: '/analytics' },
    { id: 'data', icon: <FiDatabase />, label: 'Data Streams', path: '/dataStreams' },
    { id: 'settings', icon: <FiSettings />, label: 'Settings', path: '/settings' },
  ];

  return (
    <div
      className={`fixed inset-y-0 left-0 z-50 bg-black text-white w-64 transform ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0 transition-transform duration-300`}
    >
      <div className="p-6">
        <h1 className="text-2xl font-bold flex items-center">
          <img src={logo} alt="QuantAnalytics" className="h-8 w-auto mr-2" />
          Quant<span className="text-cyan-400">Analytics</span>
        </h1>
      </div>
      <nav className="mt-8">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => {
              navigate(item.path);
              setSidebarOpen(false); // Close sidebar on mobile
            }}
            className={`w-full flex items-center px-6 py-3 text-sm hover:bg-gray-800 ${
              location.pathname === item.path ? 'bg-gray-800 border-r-4 border-cyan-400' : ''
            }`}
          >
            <span className="mr-3">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
    </div>
  );
};

Sidebar.propTypes = {
  sidebarOpen: PropTypes.bool.isRequired,
  setSidebarOpen: PropTypes.func.isRequired,
};

export default Sidebar;