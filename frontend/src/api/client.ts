import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for request ID and logging
apiClient.interceptors.request.use(
  (config) => {
    // Generate request ID for tracing. Fallback to Math.random if crypto is unavailable (HTTP context)
    const requestId = typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : Math.random().toString(36).substring(2) + Date.now().toString(36);
    config.headers['X-Request-ID'] = requestId;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const getErrorMessage = (error: any): string => {
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item: any) => {
        if (typeof item === 'string') return item;
        const field = item.loc ? item.loc.filter((l: string) => l !== 'body').join('.') : '';
        return field ? `${field}: ${item.msg}` : item.msg || JSON.stringify(item);
      })
      .join('; ');
  }
  if (detail && typeof detail === 'object') {
    return detail.message || JSON.stringify(detail);
  }
  return error.message || 'An unexpected error occurred';
};

// Interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = getErrorMessage(error);
    console.error(`[API Error] ${message}`);
    
    // Optionally transform errors or handle auth expiration
    return Promise.reject(error);
  }
);

export default apiClient;
