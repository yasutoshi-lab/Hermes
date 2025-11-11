import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic request methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  // File upload
  async uploadFile<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    };

    return this.post<T>(url, formData, config);
  }
}

// Export singleton instance
const apiClient = new ApiClient();
export default apiClient;

// API endpoint functions
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<{ token: string; user: any }>('/api/login', { email, password }),

  register: (email: string, username: string, password: string) =>
    apiClient.post<{ token: string; user: any }>('/api/register', { email, username, password }),

  logout: () => apiClient.post('/api/logout'),
};

export const fileApi = {
  upload: (file: File, onProgress?: (progress: number) => void) =>
    apiClient.uploadFile<{ id: string; filename: string }>('/api/file', file, onProgress),
};

export const taskApi = {
  create: (data: any) => apiClient.post<{ id: string }>('/api/task/summary', data),

  schedule: (data: any) => apiClient.post<{ id: string }>('/api/task/schedule', data),

  get: (id: string) => apiClient.get<any>(`/api/task/${id}`),

  list: () => apiClient.get<any[]>('/api/tasks'),
};

export const modelApi = {
  list: () => apiClient.get<string[]>('/api/models'),
};
