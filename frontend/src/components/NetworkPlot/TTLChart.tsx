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

interface TTLChartProps {
  chartData: ChartDataPoint[];
  maxPoints: number;
}

const TTLChart: React.FC<TTLChartProps> = ({ chartData, maxPoints }) => {
  const STATIC_TTL_DOMAIN = [0, 128]; // TTL typically ranges from 1-128

  // Optimize data for smooth scrolling - show only last 100 points
  const optimizedData = useMemo(() => {
    if (chartData.length <= 100) return chartData;
    return chartData.slice(-100);
  }, [chartData]);

  return (
    <div className="chart-section">
      <h3>TTL (Time To Live) - Hops</h3>
      <div className="plot-container" style={{ width: '100%', height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={optimizedData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <StaticXAxis maxPoints={maxPoints} />
            <YAxis 
              name="TTL (Hops)"
              tick={{ fontSize: 12 }}
              domain={STATIC_TTL_DOMAIN}
              type="number"
              tickCount={5}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* TTL Line - straight lines */}
            <Line
              type="linear"
              dataKey="ttl"
              stroke="#8884d8"
              strokeWidth={2}
              dot={false}
              name="TTL"
              connectNulls={false}
              isAnimationActive={false}
            />
            
            {/* Failed pings markers for TTL */}
            <Scatter
              data={optimizedData.filter(d => d.ttl === null)}
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

export default TTLChart; 