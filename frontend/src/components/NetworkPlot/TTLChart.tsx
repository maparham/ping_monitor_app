import React from 'react';
import { ChartDataPoint } from '../../types/NetworkStats';
import BaseChart from './BaseChart';
import { CHART_CONFIG } from '../../constants';

interface TTLChartProps {
  chartData: ChartDataPoint[];
  maxPoints: number;
}

const TTLChart: React.FC<TTLChartProps> = ({ chartData, maxPoints }) => {
  const config = CHART_CONFIG.TTL;

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
    />
  );
};

export default TTLChart; 