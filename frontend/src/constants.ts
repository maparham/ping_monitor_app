// API Configuration
export const API_BASE_URL = 'http://localhost:5000';

// Polling Configuration
export const POLLING_INTERVAL = 1000; // 1 second

// Plot Configuration
export const PLOT_HEIGHT = 600;
export const PLOT_MARGIN = {
  top: 120,
  bottom: 120,
  left: 80,
  right: 80,
  pad: 4
};

// Resize Debounce
export const RESIZE_DEBOUNCE_MS = 250;

// Error Messages
export const ERROR_MESSAGES = {
  FETCH_DATA: 'Failed to fetch data',
  RESET_STATS: 'Failed to reset statistics',
  FETCH_CONFIG: 'Failed to fetch config'
} as const; 