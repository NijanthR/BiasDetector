/**
 * API Service - Axios client for backend communication
 */
import axios from 'axios';

let rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').trim();
rawBaseUrl = rawBaseUrl.replace(/\/+$/, '');
// Ensure the base URL always points to the /api endpoint
const API_BASE_URL = rawBaseUrl.endsWith('/api') ? rawBaseUrl : `${rawBaseUrl}/api`;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2-minute timeout for Render free tier cold starts
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

// Response interceptor with automatic retry on cold-start errors (502, 503, 504, Network Error)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    
    // Only retry GET requests or idempotent requests if it's a server wake-up issue
    if (config && (!config._retryCount || config._retryCount < 2)) {
      const isColdStartError = 
        !error.response || 
        [502, 503, 504].includes(error.response.status) || 
        error.code === 'ECONNABORTED';

      if (isColdStartError && (!config.method || config.method.toLowerCase() === 'get')) {
        config._retryCount = (config._retryCount || 0) + 1;
        console.warn(`[API] Server wake-up in progress. Retrying request (${config._retryCount}/2)...`);
        await new Promise((resolve) => setTimeout(resolve, 3000));
        return api(config);
      }
    }

    console.error('API Error:', error.response?.data || error.message);
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
