import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    const isAuthRequest = originalRequest.url.includes('/users/login/') || originalRequest.url.includes('/users/register/');

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthRequest) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error("No refresh token");

        const response = await axios.post(
          'http://127.0.0.1:8000/api/users/refresh/',
          { refresh: refreshToken }
        );

        localStorage.setItem('access_token', response.data.access);
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

        return api(originalRequest);
      } catch (err) {
        localStorage.clear();
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export default api;