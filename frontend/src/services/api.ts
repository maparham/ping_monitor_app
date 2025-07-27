import axios from 'axios';
import { ApiResponse, ResetResponse, Config } from '../types/NetworkStats';

const API_BASE_URL = 'http://localhost:5000';

export const apiService = {
  async getData(): Promise<ApiResponse> {
    const response = await axios.get(`${API_BASE_URL}/api/data`);
    return response.data;
  },

  async getConfig(): Promise<Config> {
    const response = await axios.get(`${API_BASE_URL}/api/config`);
    return response.data;
  },

  async resetStatistics(): Promise<ResetResponse> {
    const response = await axios.post(`${API_BASE_URL}/api/reset`);
    return response.data;
  }
}; 