import { useMemo } from 'react';
import { ChartDataPoint } from '../types/NetworkStats';

export const useChartData = (chartData: ChartDataPoint[], maxPoints: number = 100) => {
  // Optimize data for smooth scrolling - show only last N points
  const optimizedData = useMemo(() => {
    if (chartData.length <= maxPoints) return chartData;
    return chartData.slice(-maxPoints);
  }, [chartData, maxPoints]);

  // Ensure we always have some data to display, even if all pings failed
  const displayData = useMemo(() => {
    if (optimizedData.length === 0) {
      // Create a dummy data point to show empty chart state
      return [{
        index: 0,
        pingTime: null,
        ttl: null,
        timestamp: Date.now()
      }];
    }
    return optimizedData;
  }, [optimizedData]);

  return {
    optimizedData,
    displayData
  };
}; 