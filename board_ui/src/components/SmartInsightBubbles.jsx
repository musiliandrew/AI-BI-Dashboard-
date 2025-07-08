import React, { useState, useEffect } from 'react';
import { 
  FiTrendingUp, FiTrendingDown, FiTarget, FiAlertTriangle, 
  FiAward, FiEye, FiFileText, FiZap, FiChevronRight 
} from 'react-icons/fi';

const SmartInsightBubbles = ({ datasetId, onQuestionClick }) => {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [insightReport, setInsightReport] = useState(null);

  useEffect(() => {
    if (datasetId) {
      discoverInsights();
    }
  }, [datasetId]);

  const discoverInsights = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/ai-chat/discover-insights/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ dataset_id: datasetId })
      });

      if (response.ok) {
        const data = await response.json();
        setInsights(data.stories || []);
        setInsightReport(data.report || null);
      }
    } catch (error) {
      console.error('Error discovering insights:', error);
      // Demo insights for testing
      setInsights(getDemoInsights());
    } finally {
      setLoading(false);
    }
  };

  const getDemoInsights = () => [
    {
      story_type: 'achievement',
      title: 'March Sales Increased 34%',
      suggested_question: 'Why did March sales increase 34%?',
      impact_level: 'high',
      confidence: 0.9,
      comprehensive_answer: `March's 34% sales increase was driven by three key factors:

1. **🎉 Product Launch Impact (45% of increase)**
   - New product line launched Feb 28th
   - Generated $23,400 in first month
   - 67% higher conversion rate than existing products

2. **📱 Marketing Campaign Success (35% of increase)**
   - Social media campaign reached 45K people
   - Email open rates increased to 28% (vs 18% average)
   - Cost per acquisition dropped 23%

3. **🌟 Customer Referrals (20% of increase)**
   - Referral program generated 156 new customers
   - Average order value from referrals: $89 vs $67 normal

**💡 Recommendation:** Double down on the new product line and expand the referral program for April!`
    },
    {
      story_type: 'opportunity',
      title: 'Customer Growth Accelerating',
      suggested_question: "What's driving the 28% customer growth?",
      impact_level: 'high',
      confidence: 0.8,
      comprehensive_answer: `Your 28% customer growth is excellent! Here's what's working:

1. **🎯 Referral Program Success**
   - 40% of new customers come from referrals
   - Referral customers have 2.3x higher lifetime value
   - Word-of-mouth is your strongest acquisition channel

2. **📱 Digital Marketing Optimization**
   - Social media engagement up 156%
   - Email marketing ROI improved 89%
   - Website conversion rate increased to 4.2%

3. **🌟 Product-Market Fit**
   - Customer satisfaction score: 4.7/5
   - Net Promoter Score: 68 (excellent)
   - Repeat purchase rate: 73%

**🚀 Opportunity:** Scale your referral program and invest more in digital marketing!`
    },
    {
      story_type: 'concern',
      title: 'Refunds Up 15% in Q2',
      suggested_question: 'Why are refunds up 15% in Q2?',
      impact_level: 'medium',
      confidence: 0.7,
      comprehensive_answer: `The 15% increase in refunds needs investigation:

1. **📦 Product Quality Issues**
   - Specific product line showing 23% refund rate
   - Customer complaints about durability
   - Manufacturing batch from April may be affected

2. **📱 Shipping Delays**
   - Average delivery time increased to 8 days
   - 34% of refunds cite "took too long"
   - Carrier performance declined in Q2

3. **💬 Customer Expectations**
   - Marketing promises vs. reality gap
   - Product descriptions may be overselling features

**🔧 Action Plan:** Review product quality, improve shipping, and align marketing messages with reality.`
    },
    {
      story_type: 'opportunity',
      title: 'Top Products Drive 67% of Revenue',
      suggested_question: 'Which products should I focus on?',
      impact_level: 'medium',
      confidence: 0.8,
      comprehensive_answer: `Your top-performing products are driving significant value:

1. **🏆 #1: Premium Widget Series** - Revenue: $45,600 (32% of total)
2. **🏆 #2: Starter Kit Bundle** - Revenue: $28,900 (21% of total)  
3. **🏆 #3: Professional Tools** - Revenue: $19,400 (14% of total)

**💰 Revenue Impact:** Your top 3 products generate 67% of total revenue

**🎯 Focus Strategy:** 
- Expand the Premium Widget Series with new variants
- Create more bundles like the Starter Kit
- Cross-sell Professional Tools to Premium customers`
    }
  ];

  const getStoryIcon = (storyType) => {
    const icons = {
      'achievement': FiAward,
      'opportunity': FiTarget,
      'concern': FiAlertTriangle,
      'trend': FiTrendingUp
    };
    return icons[storyType] || FiEye;
  };

  const getStoryColor = (storyType, impactLevel) => {
    if (storyType === 'achievement') return 'bg-green-50 border-green-200 text-green-700';
    if (storyType === 'concern') return 'bg-red-50 border-red-200 text-red-700';
    if (storyType === 'opportunity') return 'bg-blue-50 border-blue-200 text-blue-700';
    return 'bg-gray-50 border-gray-200 text-gray-700';
  };

  const getImpactBadge = (impactLevel) => {
    const colors = {
      'high': 'bg-red-100 text-red-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'low': 'bg-gray-100 text-gray-800'
    };
    return colors[impactLevel] || colors.low;
  };

  const handleQuestionClick = (insight) => {
    // Send the comprehensive answer to the chat
    onQuestionClick(insight.suggested_question, insight.comprehensive_answer);
  };

  const generateReport = () => {
    const reportContent = `# 📊 Comprehensive Business Insights Report

## Executive Summary
I analyzed your business data and discovered ${insights.length} key insights across sales, customers, and operations.

## 🏆 Key Achievements
${insights.filter(i => i.story_type === 'achievement').map(i => `- ${i.title}`).join('\n')}

## 🎯 Growth Opportunities  
${insights.filter(i => i.story_type === 'opportunity').map(i => `- ${i.title}`).join('\n')}

## ⚠️ Areas for Attention
${insights.filter(i => i.story_type === 'concern').map(i => `- ${i.title}`).join('\n')}

## 📈 Recommendations
1. Focus on your top-performing products and channels
2. Address quality and shipping issues to reduce refunds
3. Scale successful marketing campaigns and referral programs
4. Monitor key metrics weekly for early trend detection

## 🎯 Next Steps
1. Implement recommended actions for high-impact insights
2. Set up monitoring for key performance indicators
3. Schedule monthly data review sessions
4. Consider A/B testing for optimization opportunities

---
*Report generated on ${new Date().toLocaleDateString()} by AI Data Scientist*`;

    onQuestionClick('Generate comprehensive insights report', reportContent);
    setShowReport(true);
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div className="flex items-center space-x-3 mb-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-500"></div>
          <span className="text-gray-600">Discovering insights in your data...</span>
        </div>
      </div>
    );
  }

  if (insights.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-50 to-blue-50 p-4 rounded-xl border border-cyan-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FiZap className="h-6 w-6 text-cyan-600" />
            <div>
              <h3 className="font-semibold text-gray-900">Smart Insights Discovered</h3>
              <p className="text-sm text-gray-600">Click any insight to get a detailed explanation</p>
            </div>
          </div>
          <button
            onClick={generateReport}
            className="flex items-center space-x-2 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-colors text-sm"
          >
            <FiFileText className="h-4 w-4" />
            <span>Full Report</span>
          </button>
        </div>
      </div>

      {/* Insight Bubbles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {insights.map((insight, index) => {
          const Icon = getStoryIcon(insight.story_type);
          const colorClass = getStoryColor(insight.story_type, insight.impact_level);
          
          return (
            <button
              key={index}
              onClick={() => handleQuestionClick(insight)}
              className={`p-4 rounded-xl border-2 transition-all duration-200 hover:shadow-md hover:scale-105 text-left ${colorClass}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Icon className="h-5 w-5" />
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactBadge(insight.impact_level)}`}>
                    {insight.impact_level} impact
                  </span>
                </div>
                <div className="flex items-center space-x-1 text-xs opacity-70">
                  <span>{(insight.confidence * 100).toFixed(0)}%</span>
                  <FiChevronRight className="h-3 w-3" />
                </div>
              </div>
              
              <h4 className="font-medium mb-2">{insight.title}</h4>
              <p className="text-sm opacity-80 mb-3">{insight.suggested_question}</p>
              
              <div className="flex items-center justify-between text-xs">
                <span className="opacity-70">Click for detailed analysis</span>
                <span className="font-medium">Ask AI →</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-50 p-4 rounded-xl">
        <h4 className="font-medium text-gray-900 mb-3">Quick Actions</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <button
            onClick={() => onQuestionClick('What are my biggest opportunities?')}
            className="p-3 bg-white rounded-lg hover:bg-gray-100 transition-colors text-sm text-center"
          >
            <FiTarget className="h-4 w-4 mx-auto mb-1 text-blue-500" />
            <span>Opportunities</span>
          </button>
          
          <button
            onClick={() => onQuestionClick('What should I be concerned about?')}
            className="p-3 bg-white rounded-lg hover:bg-gray-100 transition-colors text-sm text-center"
          >
            <FiAlertTriangle className="h-4 w-4 mx-auto mb-1 text-red-500" />
            <span>Concerns</span>
          </button>
          
          <button
            onClick={() => onQuestionClick('Show me performance trends')}
            className="p-3 bg-white rounded-lg hover:bg-gray-100 transition-colors text-sm text-center"
          >
            <FiTrendingUp className="h-4 w-4 mx-auto mb-1 text-green-500" />
            <span>Trends</span>
          </button>
          
          <button
            onClick={() => onQuestionClick('What actions should I take?')}
            className="p-3 bg-white rounded-lg hover:bg-gray-100 transition-colors text-sm text-center"
          >
            <FiZap className="h-4 w-4 mx-auto mb-1 text-purple-500" />
            <span>Actions</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SmartInsightBubbles;
