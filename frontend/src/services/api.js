/**
 * API Service - Axios client for backend communication
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Dataset APIs
export const datasetAPI = {
  upload: (file, name) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    
    return api.post('/datasets/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  getAll: () => api.get('/datasets/'),
  
  getOne: (id) => api.get(`/datasets/${id}/`),
  
  getDetails: (id) => api.get(`/datasets/${id}/details/`),
  
  getResults: (id) => api.get(`/datasets/${id}/results/`),
  
  analyze: (id) => api.post(`/datasets/${id}/analyze/`),
  
  getHistory: () => api.get('/datasets/history/'),
  
  delete: (id) => api.delete(`/datasets/${id}/`),
};

// Report APIs
export const reportAPI = {
  getAll: () => api.get('/reports/'),
  
  getOne: (id) => api.get(`/reports/${id}/`),
  
  getLatest: () => api.get('/reports/latest_reports/'),
  
  export: (id, format) => api.post(`/reports/${id}/export/`, { format }),
};

// Dashboard APIs
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats/'),
  
  getOverview: () => api.get('/dashboard/overview/'),

  getLogs: () => api.get('/dashboard/logs/'),
};

export default api;
