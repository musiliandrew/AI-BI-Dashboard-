// board_ui/src/components/Login.jsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Added Link
import { FiLock, FiMail, FiEye, FiEyeOff } from 'react-icons/fi'; // Added FiEye, FiEyeOff

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false); // Added for toggle
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/users/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access);
      localStorage.setItem('refresh', data.refresh);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md border border-cyan-100">
        <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
          Log In to <span className="text-cyan-500">QuantAnalytics</span>
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2 font-medium" htmlFor="email">Email</label>
            <div className="flex items-center border border-gray-200 rounded-xl px-4 py-3 bg-gray-50">
              <FiMail className="text-cyan-500 mr-3" />
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full outline-none bg-transparent text-gray-900 placeholder-gray-400"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 mb-2 font-medium" htmlFor="password">Password</label>
            <div className="flex items-center border border-gray-200 rounded-xl px-4 py-3 bg-gray-50 relative">
              <FiLock className="text-cyan-500 mr-3" />
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full outline-none bg-transparent text-gray-900 placeholder-gray-400 pr-10"
                placeholder="Enter your password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 text-cyan-500 hover:text-cyan-600"
              >
                {showPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
          </div>
          {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
          <button
            type="submit"
            className="w-full bg-cyan-500 text-white py-3 rounded-xl hover:bg-cyan-600 font-semibold transition-all duration-300 shadow-md hover:shadow-cyan-500/30"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>
        <p className="mt-6 text-gray-600 text-center">
          Don’t have an account?{' '}
          <Link to="/signup" className="text-cyan-500 hover:text-cyan-600 font-medium hover:underline">
            Sign Up
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;