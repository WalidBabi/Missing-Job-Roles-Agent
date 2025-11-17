import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import Analysis from './components/Analysis';
import JobRoles from './components/JobRoles';
import OrganizationChart from './components/OrganizationChart';
import Chatbot from './components/Chatbot';

function App() {
  console.log('App component rendering...');
  
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/roles" element={<JobRoles />} />
            <Route path="/org-chart" element={<OrganizationChart />} />
            <Route path="/chatbot" element={<Chatbot />} />
          </Routes>
        </main>
        
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-600 text-sm">
                © 2025 One Development. AI-Powered HR Analytics.
              </p>
              <div className="flex items-center space-x-4 mt-4 md:mt-0">
                <span className="text-sm text-gray-600">Powered by</span>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
                    Django
                  </span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-semibold">
                    LangGraph
                  </span>
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-semibold">
                    React
                  </span>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;

