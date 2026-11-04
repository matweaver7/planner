import axios from 'axios';

// Token is stored in memory — never in localStorage or sessionStorage
let _token: string | null = null;

export function setToken(token: string | null): void {
  _token = token;
}

export function getToken(): string | null {
  return _token;
}

export const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
});

client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 401 → clear token so UI shows login page on next protected route visit
client.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      setToken(null);
    }
    return Promise.reject(error);
  },
);
