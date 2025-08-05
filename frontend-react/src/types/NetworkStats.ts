export interface NetworkStats {
  failure_rate: number;
  avg_ping_time: number | null;
  min_ping_time: number | null;
  max_ping_time: number | null;
  avg_outage_duration: number | null;
  total_pings: number;
}

export interface Config {
  max_points: number;
  target: string;
  auto_refresh_interval: number;
  api_url: string;
}

export interface ChartDataPoint {
  index: number;
  ttl: number | null;
  pingTime: number | null;
  timestamp: number;
}

export interface ApiResponse extends NetworkStats {
  chart_data: ChartDataPoint[];
}

export interface ResetResponse {
  message: string;
} 