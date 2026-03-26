import axios from 'axios';

let API_BASE_URL = import.meta.env.VITE_API_URL;

// Validate environment variable in development
if (!API_BASE_URL) {
  if (import.meta.env.DEV) {
    console.warn('⚠️ VITE_API_URL not set, defaulting to http://localhost:5000/api');
    API_BASE_URL = 'http://localhost:5000/api';
  } else {
    throw new Error(
      'Missing required environment variable: VITE_API_URL. ' +
      'Please set this variable in your .env file for production deployments.'
    );
  }
}

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Extended AI processing timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors and token refresh
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only redirect to login if a token was present (expired/revoked session).
    // Do NOT redirect on 401s triggered by unauthenticated calls like login/register.
    if (error.response?.status === 401 && localStorage.getItem('token')) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
