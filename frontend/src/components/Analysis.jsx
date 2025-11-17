import React, { useState, useEffect } from 'react';
import { triggerAnalysis, getLatestAnalysis, getAnalysisRuns } from '../services/api';

export default function Analysis() {
  const [latestAnalysis, setLatestAnalysis] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedDepartments, setSelectedDepartments] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const departments = ['Engineering', 'Product', 'Marketing', 'Sales', 'Human Resources', 'Finance', 'Customer Support', 'Operations'];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [latestRes, historyRes] = await Promise.all([
        getLatestAnalysis().catch(() => ({ data: null })),
        getAnalysisRuns()
      ]);
      setLatestAnalysis(latestRes.data);
      setAnalysisHistory(historyRes.data.results || historyRes.data);
    } catch (error) {
      console.error('Error loading analysis data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerAnalysis = async () => {
    setAnalyzing(true);
    try {
      const depts = selectedDepartments.length > 0 ? selectedDepartments : null;
      const response = await triggerAnalysis(depts);
      setLatestAnalysis(response.data);
      await loadData();
      alert(`Analysis complete! Found ${response.data.missing_roles?.length || 0} missing roles.`);
    } catch (error) {
      console.error('Error triggering analysis:', error);
      alert('Error running analysis. Please check the console.');
    } finally {
      setAnalyzing(false);
    }
  };

  const toggleDepartment = (dept) => {
    setSelectedDepartments(prev =>
      prev.includes(dept) ? prev.filter(d => d !== dept) : [...prev, dept]
    );
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      critical: 'bg-red-500',
      high: 'bg-orange-500',
      medium: 'bg-yellow-500',
      low: 'bg-gray-500',
    };
    return colors[priority] || colors.low;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Analysis</h1>
        <p className="text-gray-600 mt-2">Identify missing job roles using multi-agent AI analysis</p>
      </div>

      {/* Trigger Analysis Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Run New Analysis</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Departments (leave empty for all)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {departments.map((dept) => (
              <button
                key={dept}
                onClick={() => toggleDepartment(dept)}
                className={`p-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedDepartments.includes(dept)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {dept}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleTriggerAnalysis}
          disabled={analyzing}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {analyzing ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Analyzing (30-60 seconds)...
            </>
          ) : (
            <>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Run AI Analysis
            </>
          )}
        </button>

        {selectedDepartments.length > 0 && (
          <p className="text-sm text-gray-600 mt-2">
            Analyzing: {selectedDepartments.join(', ')}
          </p>
        )}
      </div>

      {/* Latest Analysis Results */}
      {latestAnalysis && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Latest Analysis Results</h2>
            <span className="text-sm text-gray-600">
              {new Date(latestAnalysis.run_date).toLocaleString()}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Status</p>
              <p className="text-xl font-bold text-blue-600 capitalize">{latestAnalysis.status}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Roles Analyzed</p>
              <p className="text-xl font-bold text-green-600">{latestAnalysis.total_roles_analyzed}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Missing Roles Found</p>
              <p className="text-xl font-bold text-purple-600">{latestAnalysis.missing_roles?.length || 0}</p>
            </div>
          </div>

          {/* Recommendations */}
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Missing Roles</h3>
          
          {latestAnalysis.missing_roles && latestAnalysis.missing_roles.length > 0 ? (
            <div className="space-y-4">
              {latestAnalysis.missing_roles
                .sort((a, b) => {
                  const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
                  return priorityOrder[a.priority] - priorityOrder[b.priority];
                })
                .map((role, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="text-lg font-semibold text-gray-900">{role.recommended_role_title}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getPriorityColor(role.priority)}`}>
                            {role.priority.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                            {role.department}
                          </span>
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                            {role.recommended_headcount} {role.recommended_headcount === 1 ? 'position' : 'positions'}
                          </span>
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {role.estimated_timeline}
                          </span>
                        </div>
                      </div>
                      <div className={`w-3 h-3 rounded-full ${getPriorityBadge(role.priority)}`}></div>
                    </div>

                    <div className="mt-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Why Needed:</p>
                      <p className="text-sm text-gray-600">{role.justification}</p>
                    </div>

                    <div className="mt-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Expected Impact:</p>
                      <p className="text-sm text-gray-600">{role.expected_impact}</p>
                    </div>

                    {role.required_skills && role.required_skills.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-gray-700 mb-2">Required Skills:</p>
                        <div className="flex flex-wrap gap-2">
                          {role.required_skills.map((skill, idx) => (
                            <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
            </div>
          ) : (
            <p className="text-gray-600">No missing roles identified. Organization structure looks healthy!</p>
          )}
        </div>
      )}

      {/* Analysis History */}
      <div className="bg-white rounded-lg shadow p-6">
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="flex items-center justify-between w-full text-left"
        >
          <h2 className="text-xl font-semibold text-gray-900">Analysis History</h2>
          <svg
            className={`w-5 h-5 transition-transform ${showHistory ? 'transform rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {showHistory && (
          <div className="mt-4 space-y-2">
            {analysisHistory.slice(0, 5).map((run) => (
              <div key={run.id} className="border border-gray-200 rounded p-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Analysis #{run.id}
                  </p>
                  <p className="text-xs text-gray-600">
                    {new Date(run.run_date).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    run.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {run.status}
                  </span>
                  <span className="text-sm text-gray-600">
                    {run.missing_roles_count || 0} roles found
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

