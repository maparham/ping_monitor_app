<template>
  <BaseChart
    :chart-data="chartData"
    :max-points="maxPoints"
    :title="config.title"
    :data-key="config.dataKey"
    :failed-data-key="config.failedDataKey"
    :y-axis-name="config.yAxisName"
    :y-axis-domain="config.yAxisDomain"
    :line-color="config.lineColor"
    :line-name="config.lineName"
    :calculate-y-domain="calculateYDomain"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import BaseChart from './BaseChart.vue';
import { ChartDataPoint } from '../../types/NetworkStats';
import { CHART_CONFIG } from '../../constants';

interface Props {
  chartData: ChartDataPoint[];
  maxPoints: number;
}

defineProps<Props>();

const config = CHART_CONFIG.PING_TIME;

// Auto-scale ping time y-axis calculation
const calculateYDomain = computed(() => {
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
});
</script> 