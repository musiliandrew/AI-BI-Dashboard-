import React, { useState, useEffect, useRef } from 'react';
import {
  FiMessageCircle, FiSend, FiUser, FiBrain, FiTrendingUp,
  FiBarChart3, FiZap, FiLightbulb, FiSettings, FiUpload
} from 'react-icons/fi';
import SmartInsightBubbles from './SmartInsightBubbles';

const AIDataScientist = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [userContext, setUserContext] = useState({});
  const [suggestedActions, setSuggestedActions] = useState([]);
  const [followUpQuestions, setFollowUpQuestions] = useState([]);
  const [currentDatasetId, setCurrentDatasetId] = useState(null);
  const [showInsightBubbles, setShowInsightBubbles] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    initializeChat();
    fetchUserContext();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const initializeChat = () => {
    // Add welcome message
    const welcomeMessage = {
      id: Date.now(),
      type: 'ai',
      content: "👋 Hi! I'm your AI Data Scientist. I can help you understand your data, find insights, and make better business decisions. Upload your data and I'll automatically discover the most important questions you should be asking!",
      timestamp: new Date(),
      suggestedActions: [
        "Upload and analyze my data",
        "Show me smart insights",
        "Find growth opportunities",
        "Identify potential issues"
      ]
    };
    setMessages([welcomeMessage]);
    setSuggestedActions(welcomeMessage.suggestedActions);
  };

  const handleSmartQuestionClick = (question, comprehensiveAnswer = null) => {
    // Add user question
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: question,
      timestamp: new Date()
    };

    // Add AI response (either provided comprehensive answer or simulate processing)
    const aiMessage = {
      id: Date.now() + 1,
      type: 'ai',
      content: comprehensiveAnswer || "Let me analyze that for you...",
      timestamp: new Date(),
      isComprehensive: !!comprehensiveAnswer
    };

    setMessages(prev => [...prev, userMessage, aiMessage]);

    // If no comprehensive answer provided, send to backend
    if (!comprehensiveAnswer) {
      sendMessage(question);
    }
  };

  const fetchUserContext = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/ai-chat/context/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const context = await response.json();
        setUserContext(context);
      }
    } catch (error) {
      console.error('Error fetching user context:', error);
    }
  };

  const sendMessage = async (messageText = null) => {
    const message = messageText || inputMessage.trim();
    if (!message) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/ai-chat/quick-chat/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          message,
          business_type: userContext.business_type,
          industry: userContext.industry
        })
      });

      if (!response.ok) throw new Error('Failed to send message');
      
      const data = await response.json();
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.message,
        timestamp: new Date(),
        confidence: data.confidence,
        requiresAnalysis: data.requires_analysis,
        analysisType: data.analysis_type
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setSuggestedActions(data.suggested_actions || []);
      setFollowUpQuestions(data.follow_up_questions || []);
      setSessionId(data.session_id);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I apologize, but I'm having trouble processing your request right now. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestedAction = (action) => {
    sendMessage(action);
  };

  const handleFollowUpQuestion = (question) => {
    sendMessage(question);
  };

  const updateUserContext = async (contextData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/api/ai-chat/context/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(contextData)
      });

      if (response.ok) {
        const updatedContext = await response.json();
        setUserContext(updatedContext);
      }
    } catch (error) {
      console.error('Error updating context:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg">
                <FiBrain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Data Scientist</h1>
                <p className="text-sm text-gray-600">Your personal data analyst and business advisor</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <FiSettings className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Smart Insight Bubbles */}
        {showInsightBubbles && currentDatasetId && (
          <div className="mb-6">
            <SmartInsightBubbles
              datasetId={currentDatasetId}
              onQuestionClick={handleSmartQuestionClick}
            />
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 h-[600px] flex flex-col">
          
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex items-start space-x-3 max-w-3xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' 
                      ? 'bg-cyan-500 text-white' 
                      : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  }`}>
                    {message.type === 'user' ? <FiUser className="h-4 w-4" /> : <FiBrain className="h-4 w-4" />}
                  </div>

                  {/* Message Content */}
                  <div className={`rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-cyan-500 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    
                    {/* Confidence indicator for AI messages */}
                    {message.type === 'ai' && message.confidence && (
                      <div className="mt-2 text-xs text-gray-500">
                        Confidence: {(message.confidence * 100).toFixed(0)}%
                      </div>
                    )}
                    
                    {/* Analysis indicator */}
                    {message.requiresAnalysis && (
                      <div className="mt-2 flex items-center space-x-1 text-xs text-blue-600">
                        <FiZap className="h-3 w-3" />
                        <span>Running {message.analysisType} analysis...</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                    <FiBrain className="h-4 w-4 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Actions */}
          {suggestedActions.length > 0 && (
            <div className="px-6 py-3 border-t border-gray-100">
              <p className="text-xs text-gray-500 mb-2">Suggested actions:</p>
              <div className="flex flex-wrap gap-2">
                {suggestedActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestedAction(action)}
                    className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs rounded-full transition-colors"
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Follow-up Questions */}
          {followUpQuestions.length > 0 && (
            <div className="px-6 py-3 border-t border-gray-100">
              <p className="text-xs text-gray-500 mb-2">You might also ask:</p>
              <div className="space-y-1">
                {followUpQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleFollowUpQuestion(question)}
                    className="block w-full text-left px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 text-sm rounded-lg transition-colors"
                  >
                    <FiLightbulb className="inline h-3 w-3 mr-2" />
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="p-6 border-t border-gray-100">
            <div className="flex items-end space-x-3">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about your data..."
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none"
                  rows="1"
                  style={{ minHeight: '44px', maxHeight: '120px' }}
                />
              </div>
              <button
                onClick={() => sendMessage()}
                disabled={!inputMessage.trim() || isTyping}
                className="p-3 bg-cyan-500 text-white rounded-xl hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <FiSend className="h-4 w-4" />
              </button>
            </div>
            
            <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
              <span>Press Enter to send, Shift+Enter for new line</span>
              <div className="flex items-center space-x-4">
                <span className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>AI Ready</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => {
              setShowInsightBubbles(!showInsightBubbles);
              setCurrentDatasetId('demo-dataset-123'); // Demo dataset ID
            }}
            className={`p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-center ${
              showInsightBubbles ? 'bg-cyan-50 border-cyan-200' : 'bg-white'
            }`}
          >
            <FiZap className="h-6 w-6 text-cyan-500 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-900">Smart Insights</span>
          </button>

          <button
            onClick={() => sendMessage("Analyze my latest data")}
            className="p-4 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-center"
          >
            <FiBarChart3 className="h-6 w-6 text-green-500 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-900">Analyze Data</span>
          </button>
          
          <button 
            onClick={() => sendMessage("Show me sales trends")}
            className="p-4 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-center"
          >
            <FiTrendingUp className="h-6 w-6 text-green-500 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-900">Sales Trends</span>
          </button>
          
          <button 
            onClick={() => sendMessage("Find customer insights")}
            className="p-4 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-center"
          >
            <FiUser className="h-6 w-6 text-purple-500 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-900">Customer Insights</span>
          </button>
          
          <button 
            onClick={() => sendMessage("What should I focus on?")}
            className="p-4 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-center"
          >
            <FiLightbulb className="h-6 w-6 text-yellow-500 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-900">Get Advice</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIDataScientist;
