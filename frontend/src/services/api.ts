import axios from 'axios';
import { ApiResponse, ResetResponse, Config } from '../types/NetworkStats';
import { API_BASE_URL } from '../constants';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased from 10s to 30s to handle slow backend responses during network issues
});

export const apiService = {
  async getData(): Promise<ApiResponse> {
    const response = await apiClient.get('/api/data');
    return response.data;
  },

  async getConfig(): Promise<Config> {
    const response = await apiClient.get('/api/config');
    return response.data;
  },

  async resetStatistics(): Promise<ResetResponse> {
    const response = await apiClient.post('/api/reset');
    return response.data;
  }
}; 