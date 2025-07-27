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
  data: Plotly.Data[];
  layout: Partial<Plotly.Layout>;
}

export interface ApiResponse extends NetworkStats {
  plot_data: PlotData;
}

export interface ResetResponse {
  message: string;
} 