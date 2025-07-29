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
  />
</template>

<script setup lang="ts">
import BaseChart from './BaseChart.vue';
import { ChartDataPoint } from '../../types/NetworkStats';
import { CHART_CONFIG } from '../../constants';

interface Props {
  chartData: ChartDataPoint[];
  maxPoints: number;
}

defineProps<Props>();

const config = CHART_CONFIG.TTL;
</script> 