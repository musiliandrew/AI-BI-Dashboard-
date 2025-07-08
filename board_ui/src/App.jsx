import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Signup from "./components/signup";
import QuantAnalyticsDashboard from "./components/Dashboard";
import SignIn from "./components/login";
import AnalyticsPage from "./components/analytics";
import DataStreams from "./components/dataStreams";
import SettingsPage from "./components/settings";
import HomePage from "./components/Home";
import OrganizationDashboard from "./components/OrganizationDashboard";
import BillingPage from "./components/BillingPage";
import AdminDashboard from "./components/AdminDashboard";
import IntelligentAnalytics from "./components/IntelligentAnalytics";
import AIDataScientist from "./components/AIDataScientist";
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
        <Route path="/organization" element={<OrganizationDashboard/>} />
        <Route path="/billing" element={<BillingPage/>} />
        <Route path="/admin" element={<AdminDashboard/>} />
        <Route path="/intelligent" element={<IntelligentAnalytics/>} />
        <Route path="/ai-chat" element={<AIDataScientist/>} />
      </Routes>
    </Router>
  );
}

export default App;
