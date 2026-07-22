import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // I might need to install uuid, but let's just use standard fetch or crypto.randomUUID for request ID if available, wait, crypto.randomUUID() is built-in to modern browsers. Let's just use crypto.randomUUID().

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for request ID and logging
apiClient.interceptors.request.use(
  (config) => {
    // Generate request ID for tracing
    const requestId = crypto.randomUUID();
    config.headers['X-Request-ID'] = requestId;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // We can add global error toast notifications here
    const message = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    console.error(`[API Error] ${message}`);
    
    // Optionally transform errors or handle auth expiration
    return Promise.reject(error);
  }
);

export default apiClient;
