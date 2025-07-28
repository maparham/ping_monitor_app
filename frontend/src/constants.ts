// API Configuration
export const API_BASE_URL = 'http://localhost:5000';

// Default Polling Configuration (fallback if backend config is not available)
export const DEFAULT_POLLING_INTERVAL = 1000; // 1 second

// Error Messages
export const ERROR_MESSAGES = {
  FETCH_DATA: 'Failed to fetch data',
  RESET_STATS: 'Failed to reset statistics',
  FETCH_CONFIG: 'Failed to fetch config'
} as const; 