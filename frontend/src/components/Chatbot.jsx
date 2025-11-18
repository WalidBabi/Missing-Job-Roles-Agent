import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage, getConversations, getConversation } from '../services/api';

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "👋 Hi! I'm your HR AI assistant. I can help you:\n\n• Identify missing job roles in your organization\n• Run AI analysis on your workforce\n• Answer questions about your org structure\n• Get recommendations for hiring\n\nTry asking: \"What roles are we missing?\" or \"Run an analysis\""
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null); // Track conversation for memory
  const [conversations, setConversations] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Reload conversations when a new message is sent
  useEffect(() => {
    if (conversationId) {
      loadConversations();
    }
  }, [conversationId]);

  const loadConversations = async () => {
    try {
      setLoadingConversations(true);
      const response = await getConversations();
      setConversations(response.data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadConversationMessages = async (convId) => {
    try {
      setLoading(true);
      const response = await getConversation(convId);
      const conversationMessages = response.data.messages || [];
      
      // Convert to message format
      const formattedMessages = conversationMessages.map(msg => ({
        role: msg.role,
        content: msg.content,
        triggeredAnalysis: msg.triggered_analysis,
        recommendationsCount: 0 // Could be enhanced to track this
      }));
      
      setMessages(formattedMessages);
      setConversationId(convId);
    } catch (error) {
      console.error('Error loading conversation:', error);
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setConversationId(null);
    setMessages([
      {
        role: 'assistant',
        content: "👋 Hi! I'm your HR AI assistant. I can help you:\n\n• Identify missing job roles in your organization\n• Run AI analysis on your workforce\n• Answer questions about your org structure\n• Get recommendations for hiring\n\nTry asking: \"What roles are we missing?\" or \"Run an analysis\""
      }
    ]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(userMessage, conversationId);
      const assistantResponse = response.data.response;
      const triggeredAnalysis = response.data.triggered_analysis || false;
      const newConversationId = response.data.conversation_id;
      
      // Update conversation ID if we got a new one (first message) or if it changed
      if (newConversationId && newConversationId !== conversationId) {
        setConversationId(newConversationId);
        // Reload conversations to show the new one
        loadConversations();
      }
      
      // Add assistant response
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: assistantResponse,
        triggeredAnalysis: triggeredAnalysis,
        recommendationsCount: response.data.recommendations_count || 0
      }]);
      
      // If analysis was triggered, suggest viewing results
      if (triggeredAnalysis && response.data.recommendations_count > 0) {
        setTimeout(() => {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: "💡 **Tip:** You can view detailed recommendations in the **AI Analysis** page or see them visualized in the **Org Chart** page!"
          }]);
        }, 2000);
      }
    } catch (error) {
      console.error('Chatbot error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Sorry, I encountered an error: ${error.response?.data?.error || error.message}. Please try again.`
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    let formatted = content;
    
    // Bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Line breaks - convert to <br> tags
    formatted = formatted.replace(/\n/g, '<br />');
    
    return { __html: formatted };
  };

  const quickActions = [
    "What roles are we missing?",
    "Run an analysis",
    "Show me recommendations",
    "What departments need more people?",
  ];

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="flex gap-4">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden bg-white rounded-lg shadow-lg flex flex-col`} style={{ height: '800px' }}>
        {sidebarOpen && (
          <div className="p-4 flex flex-col flex-1 min-h-0">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Conversations</h2>
              <button
                onClick={startNewConversation}
                className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                + New
              </button>
            </div>
            
            {loadingConversations ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-600"></div>
              </div>
            ) : conversations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No conversations yet</p>
                <p className="text-sm mt-2">Start chatting to create one!</p>
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto space-y-2">
                {conversations.map((conv) => (
                  <button
                    key={conv.conversation_id}
                    onClick={() => loadConversationMessages(conv.conversation_id)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      conversationId === conv.conversation_id
                        ? 'bg-blue-50 border-blue-300'
                        : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <span className="text-xs font-medium text-gray-600">
                        {formatDate(conv.last_message_time)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {conv.message_count} msgs
                      </span>
                    </div>
                    {conv.last_message_preview && (
                      <p className="text-sm text-gray-700 line-clamp-2">
                        {conv.last_message_preview}
                      </p>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title={sidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h1 className="text-3xl font-bold text-gray-900">HR AI Assistant</h1>
            </div>
            <p className="text-gray-600 mt-2">Ask me anything about your organization's structure and missing roles</p>
          </div>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-lg shadow-lg flex flex-col" style={{ height: '600px' }}>
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                {message.role === 'assistant' ? (
                  <div
                    className="prose prose-sm max-w-none"
                    dangerouslySetInnerHTML={formatMessage(message.content)}
                  />
                ) : (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                )}
                
                {message.triggeredAnalysis && message.recommendationsCount > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-300">
                    <p className="text-xs text-gray-600">
                      ✓ Analysis completed with {message.recommendationsCount} recommendations
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                  <span className="text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        {messages.length === 1 && (
          <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
            <p className="text-xs text-gray-600 mb-2">Quick actions:</p>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setInput(action);
                    inputRef.current?.focus();
                  }}
                  className="px-3 py-1.5 text-xs bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSend} className="flex space-x-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about your organization..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
        </div>
      </div>

      {/* Info Panel */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">💡 How to use:</h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Ask questions like: "What roles are missing in Engineering?"</li>
          <li>Request analysis: "Run an analysis" or "Analyze the organization"</li>
          <li>Get recommendations: "Show me critical missing roles"</li>
          <li>Ask follow-up questions about any recommendations</li>
        </ul>
      </div>
      </div>
    </div>
  );
}

