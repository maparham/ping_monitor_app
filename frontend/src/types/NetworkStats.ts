export interface NetworkStats {
  failure_rate: number;
  avg_ping_time: number | null;
  min_ping_time: number | null;
  max_ping_time: number | null;
  avg_failed_pings: number;
  total_pings: number;
}

export interface Config {
  max_points: number;
  num_windows: number;
  target: string;
}

export interface PlotData {
  data: any[];
  layout: any;
}

export interface ApiResponse {
  plot_data: PlotData;
  failure_rate: number;
  avg_ping_time: number | null;
  min_ping_time: number | null;
  max_ping_time: number | null;
  avg_failed_pings: number;
  total_pings: number;
}

export interface ResetResponse {
  message: string;
} 