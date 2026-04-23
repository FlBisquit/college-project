import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // For session cookies
});

// Fetch CSRF token
const getCsrfToken = async () => {
  const response = await axios.get('/api/csrf/', { withCredentials: true });
  return response.data.csrfToken;
};

// Add CSRF token to requests
api.interceptors.request.use(async (config) => {
  if (config.method !== 'get') {
    try {
      const csrfToken = await getCsrfToken();
      config.headers['X-CSRFToken'] = csrfToken;
    } catch (error) {
      console.error('Failed to get CSRF token:', error);
    }
  }
  return config;
});

export default api;