<template>
  <div class="chart-section">
    <h3>{{ title }}</h3>
    <div class="plot-container">
                       <Line
                   v-if="chartData.datasets.length > 0"
                   :key="`${title}-${props.chartData.length}-${Date.now()}`"
                   :data="chartData"
                   :options="chartOptions"
                 />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { ChartDataPoint } from '../../types/NetworkStats';
import { FAILED_PING_MARK } from '../../constants';


ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface Props {
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

const props = defineProps<Props>();





// Calculate Y domain (either static or dynamic)
const yDomain = computed(() => {
  if (props.calculateYDomain) {
    const recentData = props.chartData.slice(-props.maxPoints);
    return props.calculateYDomain(recentData);
  }
  return props.yAxisDomain;
});

  // Create chart data with failed pings as separate dataset
const chartData = computed(() => {
  // Use the last maxPoints from the original data
  const recentData = props.chartData.slice(-props.maxPoints);
  const validData = recentData.filter(d => d[props.dataKey as keyof ChartDataPoint] !== null);
  const failedData = recentData.filter(d => d[props.dataKey as keyof ChartDataPoint] === null);
  
  const datasets = [
    {
      label: props.lineName,
      data: validData.map(d => ({
        x: d.index,
        y: d[props.dataKey as keyof ChartDataPoint] as number
      })),
      borderColor: props.lineColor,
      backgroundColor: props.lineColor,
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.1
    }
  ];

  // Add failed pings as separate dataset
  if (failedData.length > 0) {
    datasets.push({
      label: FAILED_PING_MARK.NAME,
      data: failedData.map(d => ({
        x: d.index,
        y: yDomain.value[1] // Place at top of chart
      })),
      borderColor: FAILED_PING_MARK.STROKE_COLOR,
      backgroundColor: FAILED_PING_MARK.FILL_COLOR,
      borderWidth: FAILED_PING_MARK.STROKE_WIDTH,
      pointRadius: FAILED_PING_MARK.RADIUS,
      tension: 0.1
    });
  }

  return {
    datasets
  };
});

const chartOptions = computed((): ChartOptions<'line'> => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  scales: {
                   x: {
                 type: 'linear',
                 position: 'bottom',
                 min: Math.max(0, props.chartData.length - props.maxPoints),
                 max: props.chartData.length - 1,
                 ticks: {
                   stepSize: Math.max(1, Math.floor(props.maxPoints / 10))
                 }
               },
    y: {
      type: 'linear',
      position: 'left',
      min: yDomain.value[0],
      max: yDomain.value[1],
      title: {
        display: true,
        text: props.yAxisName
      }
    }
  },
  plugins: {
    legend: {
      display: true,
      position: 'top'
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      callbacks: {
                           title: (context) => {
                     const dataIndex = context[0]?.dataIndex;
                     if (dataIndex !== undefined) {
                       const recentData = props.chartData.slice(-props.maxPoints);
                       const dataPoint = recentData[dataIndex];
                       if (dataPoint) {
                         return `Index: ${dataPoint.index}`;
                       }
                     }
                     return '';
                   },
                   label: (context) => {
                     const dataIndex = context.dataIndex;
                     if (dataIndex !== undefined) {
                       const recentData = props.chartData.slice(-props.maxPoints);
                       const dataPoint = recentData[dataIndex];
                       if (dataPoint) {
                         const timestamp = new Date(dataPoint.timestamp).toLocaleTimeString();
                         return `${context.dataset.label}: ${context.parsed.y} (${timestamp})`;
                       }
                     }
                     return '';
                   }
      }
    }
  }
}));


</script>

<style scoped>
.chart-section {
  margin-bottom: 2rem;
}

.chart-section h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1.1rem;
  text-align: center;
}

.plot-container {
  width: 100%;
  height: 300px;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style> 