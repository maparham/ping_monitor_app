import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Scatter
} from 'recharts';
import { ChartDataPoint } from '../../types/NetworkStats';
import { StaticXAxis } from './StaticXAxis';
import { CustomTooltip } from './CustomTooltip';

interface PingTimeChartProps {
  chartData: ChartDataPoint[];
  maxPoints: number;
}

const PingTimeChart: React.FC<PingTimeChartProps> = ({ chartData, maxPoints }) => {
  // Optimize data for smooth scrolling - show only last 100 points
  const optimizedData = useMemo(() => {
    if (chartData.length <= 100) return chartData;
    return chartData.slice(-100);
  }, [chartData]);

  // Auto-scale ping time y-axis
  const pingYDomain = useMemo(() => {
    const validPings = optimizedData.map(d => d.pingTime).filter((v): v is number => v !== null && !isNaN(v));
    if (validPings.length === 0) return [0, 100];
    const min = Math.min(...validPings);
    const max = Math.max(...validPings);
    // Add 10% padding above and below
    const range = max - min || 10;
    const pad = Math.max(range * 0.1, 5);
    return [Math.max(0, Math.floor(min - pad)), Math.ceil(max + pad)];
  }, [optimizedData]);

  return (
    <div className="chart-section">
      <h3>Ping Time - Response Time</h3>
      <div className="plot-container" style={{ width: '100%', height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={optimizedData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <StaticXAxis maxPoints={maxPoints} />
            <YAxis 
              name="Ping Time (ms)"
              tick={{ fontSize: 12 }}
              domain={pingYDomain}
              type="number"
              tickCount={5}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Ping Time Line - straight lines */}
            <Line
              type="linear"
              dataKey="pingTime"
              stroke="#82ca9d"
              strokeWidth={2}
              dot={false}
              name="Ping Time"
              connectNulls={false}
              isAnimationActive={false}
            />
            
            {/* Failed pings markers for Ping Time */}
            <Scatter
              data={optimizedData.filter(d => d.pingTime === null)}
              fill="#ff0000"
              shape="cross"
              name="Failed Pings"
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PingTimeChart; 