// board_ui/src/components/HomePage.jsx
import { 
  ChartBarIcon, 
  CpuChipIcon, 
  CloudArrowUpIcon,
  LightBulbIcon,
  UserGroupIcon,
  ClockIcon,
  DocumentChartBarIcon,
  PlayCircleIcon,
  ArrowPathIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom'; // Import Link for navigation
import bgImage from "../assets/bg_image.jpg";

const HomePage = () => {
return (
  <div className="bg-gray-50">
    {/* Navigation */}
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <h1 className="text-2xl font-bold">Quant<span className="text-cyan-400">Analytics</span></h1>
          <div className="hidden md:flex space-x-8">
            <a href="#features" className="text-gray-700 hover:text-cyan-600">Features</a>
            <a href="#testimonials" className="text-gray-700 hover:text-cyan-600">Testimonials</a>
            <a href="#pricing" className="text-gray-700 hover:text-cyan-600">Pricing</a>
          </div>
          <Link to="/signup" className="bg-cyan-500 text-white px-6 py-2.5 rounded-lg hover:bg-cyan-600 font-semibold transition-colors">
            Start Free Trial
          </Link>
        </div>
      </div>
    </nav>

    {/* Hero Section */}
    <div className="relative isolate overflow-hidden">
      <div 
        className="absolute inset-0 -z-10 opacity-90"
        style={{
          backgroundImage: `linear-gradient(to right bottom, rgba(6, 182, 212, 0.15), rgba(34, 211, 238, 0.1)), url(${bgImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32 text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          <span className="bg-gradient-to-r from-cyan-400 to-cyan-600 bg-clip-text text-transparent">
            AI-Powered Insights
          </span>
          <br />
          for Smarter Business Decisions
        </h1>
        
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          Advanced business intelligence dashboard leveraging AI and machine learning for predictive analytics and data-driven recommendations
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link 
            to="/signup" 
            className="bg-cyan-500 text-white px-8 py-4 rounded-xl hover:bg-cyan-600 font-semibold
                       transition-all duration-300 shadow-lg hover:shadow-cyan-500/30 flex items-center gap-2"
          >
            Get Started
            <ArrowPathIcon className="w-5 h-5" />
          </Link>
          
          <a 
            href="#" 
            className="bg-white text-gray-900 px-8 py-4 rounded-xl border border-gray-200 hover:border-cyan-400
                       font-semibold transition-all duration-300 shadow-sm hover:shadow-md flex items-center gap-2"
          >
            <PlayCircleIcon className="w-5 h-5 text-cyan-500" />
            See It in Action
          </a>
        </div>

        {/* Animated Dashboard Preview */}
        <div className="mt-16 mx-auto max-w-5xl bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-4 border border-gray-200">
          <div className="bg-gradient-to-br from-cyan-100 to-cyan-50 rounded-lg h-64 animate-pulse-fast">
            <div className="flex justify-center items-center h-full text-cyan-500">
              <DocumentChartBarIcon className="w-16 h-16" />
            </div>
          </div>
        </div>
      </div>
    </div>

    {/* Features Grid */}
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Why Choose AI-Driven Business Intelligence?
          </h2>
          <p className="text-gray-600 max-w-xl mx-auto">
            Transform raw data into actionable insights with our cutting-edge features
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            { icon: ChartBarIcon, title: 'Predictive Analytics', desc: 'Forecast trends with AI models' },
            { icon: LightBulbIcon, title: 'Automated Insights', desc: 'AI detects patterns & anomalies instantly' },
            { icon: UserGroupIcon, title: 'Customer Segmentation', desc: 'Understand buying behavior using ML' },
            { icon: ClockIcon, title: 'Real-Time Dashboards', desc: 'Interactive graphs & business KPIs' },
            { icon: DocumentChartBarIcon, title: 'Custom Reports', desc: 'Generate AI-powered reports' },
            { icon: CpuChipIcon, title: 'API Integrations', desc: 'Sync with existing business tools' },
          ].map((feature, idx) => (
            <div 
              key={idx}
              className="group bg-gray-50 p-8 rounded-2xl transition-all hover:bg-cyan-50 hover:-translate-y-2"
            >
              <div className="w-14 h-14 bg-cyan-100 rounded-xl flex items-center justify-center mb-6">
                <feature.icon className="w-6 h-6 text-cyan-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-gray-600">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* How It Works Section */}
    <section className="py-20 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            How Our AI-Powered Dashboard Works
          </h2>
          <p className="text-gray-600 max-w-xl mx-auto">
            Simple 4-step process to transform your business data
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-8">
          {[
            { icon: CloudArrowUpIcon, title: 'Upload Data', desc: 'Drag & drop files or connect databases' },
            { icon: CpuChipIcon, title: 'AI Analysis', desc: 'Cleans, processes & applies ML models' },
            { icon: LightBulbIcon, title: 'Get Insights', desc: 'Predictive analytics & business trends' },
            { icon: ChartBarIcon, title: 'Take Action', desc: 'Make informed decisions with AI-backed recs' },
          ].map((step, idx) => (
            <div key={idx} className="text-center p-6">
              <div className="w-20 h-20 bg-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-white text-2xl font-bold">{idx + 1}.</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
              <p className="text-gray-600">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Testimonials Section */}
    <section id="testimonials" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Trusted by Data-Driven Businesses
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-gray-50 p-8 rounded-2xl">
            <p className="text-gray-600 mb-4">
              &quot;This AI-powered dashboard transformed our decision-making process! We&apos;ve increased operational efficiency by 40%.&quot;
            </p>
            <div className="flex items-center">
              <div className="w-12 h-12 bg-cyan-100 rounded-full mr-4"></div>
              <div>
                <h4 className="font-semibold">Sarah Johnson</h4>
                <p className="text-gray-600 text-sm">CEO, TechCorp</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 p-8 rounded-2xl">
            <p className="text-gray-600 mb-4">
              &quot;We reduced operational costs by 30% using predictive insights. The ROI was immediate and significant.&quot;
            </p>
            <div className="flex items-center">
              <div className="w-12 h-12 bg-cyan-100 rounded-full mr-4"></div>
              <div>
                <h4 className="font-semibold">Michael Chen</h4>
                <p className="text-gray-600 text-sm">CFO, FinTech Solutions</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* Pricing Section */}
    <section id="pricing" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Flexible Pricing Plans
          </h2>
          <p className="text-gray-600 max-w-xl mx-auto">
            Start with a free trial and scale as you grow
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            { 
              name: 'Starter',
              price: 'Free',
              desc: 'Perfect for small teams',
              features: ['Basic Analytics', '3 Team Members', '5GB Storage', 'Email Support']
            },
            { 
              name: 'Business',
              price: '$99',
              desc: 'For growing organizations',
              features: ['Advanced Analytics', '10 Team Members', '50GB Storage', 'Priority Support', 'API Access']
            },
            { 
              name: 'Enterprise',
              price: 'Custom',
              desc: 'Tailored solutions',
              features: ['Custom Analytics', 'Unlimited Users', '1TB Storage', '24/7 Support', 'Dedicated SLAs']
            },
          ].map((plan, idx) => (
            <div 
              key={idx}
              className={`p-8 rounded-2xl ${plan.name === 'Business' ? 'bg-cyan-500 text-white' : 'bg-white'} 
                transition-all hover:shadow-xl`}
            >
              <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
              <div className="text-4xl font-bold mb-4">{plan.price}</div>
              <p className="mb-6">{plan.desc}</p>
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, fIdx) => (
                  <li key={fIdx} className="flex items-center">
                    <ShieldCheckIcon className={`w-5 h-5 mr-2 ${plan.name === 'Business' ? 'text-white' : 'text-cyan-500'}`} />
                    {feature}
                  </li>
                ))}
              </ul>
              <button className={`w-full py-3 rounded-lg font-semibold 
                ${plan.name === 'Business' ? 
                  'bg-white text-cyan-500 hover:bg-gray-100' : 
                  'bg-cyan-500 text-white hover:bg-cyan-600'}`}
              >
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Final CTA */}
    <div className="bg-cyan-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-3xl font-bold text-white mb-6">
          Start Your AI Analytics Journey Today
        </h2>
        <p className="text-cyan-100 mb-8 max-w-xl mx-auto">
          Join thousands of companies transforming their business with data-driven insights
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link 
            to="/signup" 
            className="bg-white text-cyan-600 px-8 py-4 rounded-lg hover:bg-gray-100 font-semibold
                       transition-all duration-300 shadow-lg"
          >
            Start Free Trial
          </Link>
          <a 
            href="#" 
            className="bg-cyan-600 text-white px-8 py-4 rounded-lg hover:bg-cyan-700 font-semibold
                       transition-all duration-300 shadow-lg"
          >
            Schedule Demo
          </a>
        </div>
      </div>
    </div>

    {/* Footer */}
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
          <div className="md:col-span-2">
            <h3 className="text-white text-xl font-bold mb-4">QuantAnalytics</h3>
            <p className="text-sm">AI-powered business intelligence platform transforming data into strategic insights</p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#features" className="hover:text-cyan-400 transition-colors">Features</a></li>
              <li><a href="#pricing" className="hover:text-cyan-400 transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Integrations</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-cyan-400 transition-colors">About</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Careers</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Privacy</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Terms</a></li>
              <li><a href="#" className="hover:text-cyan-400 transition-colors">Security</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-12 pt-8 text-center text-sm">
          © 2024 QuantAnalytics. All rights reserved.
        </div>
      </div>
    </footer>
  </div>
);
};

export default HomePage;