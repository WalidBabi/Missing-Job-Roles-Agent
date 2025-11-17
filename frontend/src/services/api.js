import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Job Roles API
export const getJobRoles = () => api.get('/job-roles/');
export const getJobRoleStats = () => api.get('/job-roles/statistics/');
export const getJobRolesByDepartment = () => api.get('/job-roles/by_department/');
export const getOrgChart = () => api.get('/job-roles/org_chart/');

// Employees API
export const getEmployees = () => api.get('/employees/');
export const getWorkloadStats = () => api.get('/employees/workload_stats/');

// Analysis API
export const getAnalysisRuns = () => api.get('/analysis-runs/');
export const getLatestAnalysis = () => api.get('/analysis-runs/latest/');
export const getAnalysisById = (id) => api.get(`/analysis-runs/${id}/`);
export const triggerAnalysis = (departments = null) => {
  const data = departments ? { departments } : {};
  return api.post('/analysis-runs/trigger/', data);
};

// Missing Roles API
export const getMissingRoles = () => api.get('/missing-roles/');
export const getMissingRolesByPriority = () => api.get('/missing-roles/by_priority/');
export const getMissingRolesByDepartment = () => api.get('/missing-roles/by_department/');

// Chatbot API
export const sendChatMessage = (message, conversationId = null) => {
  return api.post('/chatbot/', { message, conversation_id: conversationId });
};

export default api;

