import React from 'react';
import { ChartDataPoint } from '../../types/NetworkStats';
import TTLChart from './TTLChart';
import PingTimeChart from './PingTimeChart';

interface NetworkPlotProps {
  chartData: ChartDataPoint[];
  maxPoints?: number;
}

const NetworkPlot: React.FC<NetworkPlotProps> = ({ chartData, maxPoints = 300 }) => {
  return (
    <div className="charts-container">
      <TTLChart chartData={chartData} maxPoints={maxPoints} />
      <PingTimeChart chartData={chartData} maxPoints={maxPoints} />
    </div>
  );
};

export default NetworkPlot; 