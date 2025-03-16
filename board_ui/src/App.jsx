import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Signup from "./components/signup";
import QuantAnalyticsDashboard from "./components/Dashboard";
import SignIn from "./components/login";
import AnalyticsPage from "./components/analytics";
import DataStreams from "./components/dataStreams";
import SettingsPage from "./components/settings";
import HomePage from "./components/Home";
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<QuantAnalyticsDashboard />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<SignIn />} />
        <Route path="/analytics" element={<AnalyticsPage/>} />
        <Route path="/dataStreams" element={<DataStreams/>} />
        <Route path="/settings" element={<SettingsPage/>} />
      </Routes>
    </Router>
  );
}

export default App;
