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
import { FailedPingShape } from './FailedPingShape';
import { FAILED_PING_MARK } from '../../constants';
import { useChartData } from '../../hooks/useChartData';

interface BaseChartProps {
  chartData: ChartDataPoint[];
  maxPoints: number;
  title: string;
  dataKey: string;
  failedDataKey: string;
  yAxisName: string;
  yAxisDomain: [number, number];
  lineColor: string;
  lineName: string;
  calculateYDomain?: (data: ChartDataPoint[]) => [number, number];
}

const BaseChart: React.FC<BaseChartProps> = ({
  chartData,
  maxPoints,
  title,
  dataKey,
  failedDataKey,
  yAxisName,
  yAxisDomain,
  lineColor,
  lineName,
  calculateYDomain
}) => {
  const { optimizedData, displayData } = useChartData(chartData, 100);

  // Calculate Y domain (either static or dynamic)
  const yDomain = useMemo(() => {
    if (calculateYDomain) {
      return calculateYDomain(optimizedData);
    }
    return yAxisDomain;
  }, [optimizedData, yAxisDomain, calculateYDomain]);

  // Create separate data for failed pings with a dummy value for visualization
  const failedPingsData = useMemo(() => {
    const [minY, maxY] = yDomain;
    const midY = (minY + maxY) / 2;
    
    return optimizedData.filter(d => d[dataKey as keyof ChartDataPoint] === null).map(d => ({
      ...d,
      [failedDataKey]: midY // Use a separate field for failed pings
    }));
  }, [optimizedData, yDomain, dataKey, failedDataKey]);

  // Create custom shape function for this specific chart
  const CustomFailedPingShape = (props: any) => (
    <FailedPingShape {...props} dataKey={failedDataKey} />
  );

  return (
    <div className="chart-section">
      <h3>{title}</h3>
      <div className="plot-container" style={{ width: '100%', height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={displayData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <StaticXAxis maxPoints={maxPoints} />
            <YAxis 
              name={yAxisName}
              tick={{ fontSize: 12 }}
              domain={yDomain}
              type="number"
              tickCount={5}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Main Line */}
            <Line
              type="linear"
              dataKey={dataKey}
              stroke={lineColor}
              strokeWidth={2}
              dot={false}
              name={lineName}
              connectNulls={false}
              isAnimationActive={false}
            />
            
            {/* Failed pings as a separate scatter series with custom shape */}
            <Scatter
              data={failedPingsData}
              fill={FAILED_PING_MARK.FILL_COLOR}
              shape={CustomFailedPingShape}
              name={FAILED_PING_MARK.NAME}
              isAnimationActive={false}
              dataKey={failedDataKey}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default BaseChart; 