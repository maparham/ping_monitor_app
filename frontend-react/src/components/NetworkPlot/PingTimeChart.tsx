import React, { useMemo } from 'react';
import { ChartDataPoint } from '../../types/NetworkStats';
import BaseChart from './BaseChart';
import { CHART_CONFIG } from '../../constants';

interface PingTimeChartProps {
  chartData: ChartDataPoint[];
  maxPoints: number;
}

const PingTimeChart: React.FC<PingTimeChartProps> = ({ chartData, maxPoints }) => {
  // Auto-scale ping time y-axis calculation
  const calculateYDomain = useMemo(() => {
    return (data: ChartDataPoint[]): [number, number] => {
      const validPings = data.map(d => d.pingTime).filter((v): v is number => v !== null && !isNaN(v));
      if (validPings.length === 0) return [0, 100];
      const min = Math.min(...validPings);
      const max = Math.max(...validPings);
      // Add 10% padding above and below
      const range = max - min || 10;
      const pad = Math.max(range * 0.1, 5);
      return [Math.max(0, Math.floor(min - pad)), Math.ceil(max + pad)];
    };
  }, []);

  const config = CHART_CONFIG.PING_TIME;

  return (
    <BaseChart
      chartData={chartData}
      maxPoints={maxPoints}
      title={config.title}
      dataKey={config.dataKey}
      failedDataKey={config.failedDataKey}
      yAxisName={config.yAxisName}
      yAxisDomain={config.yAxisDomain}
      lineColor={config.lineColor}
      lineName={config.lineName}
      calculateYDomain={calculateYDomain}
    />
  );
};

export default PingTimeChart; 