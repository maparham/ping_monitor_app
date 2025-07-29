// API Configuration
export const API_BASE_URL = 'http://localhost:5000';

// Default Polling Configuration (fallback if backend config is not available)
export const DEFAULT_POLLING_INTERVAL = 1000; // 1 second

// Failed Ping Mark Configuration
export const FAILED_PING_MARK = {
  FILL_COLOR: '#ff0000',
  STROKE_COLOR: '#ff0000',
  SHAPE: 'cross' as const,
  RADIUS: 3,
  STROKE_WIDTH: 1,
  NAME: 'Failed Pings'
} as const;

// Chart Configurations
export const CHART_CONFIG = {
  PING_TIME: {
    title: 'Ping Time - Response Time',
    dataKey: 'pingTime',
    failedDataKey: 'failedPingValue',
    yAxisName: 'Ping Time (ms)',
    yAxisDomain: [0, 100] as [number, number],
    lineColor: '#82ca9d',
    lineName: 'Ping Time'
  },
  TTL: {
    title: 'TTL (Time To Live) - Hops',
    dataKey: 'ttl',
    failedDataKey: 'failedTTLValue',
    yAxisName: 'TTL (Hops)',
    yAxisDomain: [0, 128] as [number, number],
    lineColor: '#8884d8',
    lineName: 'TTL'
  }
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  FETCH_DATA: 'Failed to fetch data',
  RESET_STATS: 'Failed to reset statistics',
  FETCH_CONFIG: 'Failed to fetch config'
} as const; 