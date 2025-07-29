<template>
  <div class="charts-container">
    <TTLChart :chart-data="chartData" :max-points="maxPoints" />
    <PingTimeChart :chart-data="chartData" :max-points="maxPoints" />
  </div>
</template>

<script setup lang="ts">
import TTLChart from './TTLChart.vue';
import PingTimeChart from './PingTimeChart.vue';
import { ChartDataPoint } from '../../types/NetworkStats';

interface Props {
  chartData: ChartDataPoint[];
  maxPoints?: number;
}

withDefaults(defineProps<Props>(), {
  maxPoints: 300
});
</script>

<style scoped>
.charts-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
</style> 