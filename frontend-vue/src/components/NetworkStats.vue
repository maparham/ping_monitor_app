<template>
  <div class="stats-box">
    <div class="stats-title">Network Statistics</div>
    <div class="stats-grid">
      <StatItem
        v-for="(item, index) in statItems"
        :key="`${item.label}-${index}`"
        :label="item.label"
        :value="item.value"
        :unit="item.unit"
        :tooltip="item.tooltip"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import StatItem from './StatItem.vue';
import type { NetworkStats as NetworkStatsType, Config } from '../types/NetworkStats';

interface Props {
  stats: NetworkStatsType;
  config: Config | null;
}

const props = defineProps<Props>();

const statItems = computed(() => [
  {
    label: 'Failure Rate',
    value: props.stats.failure_rate,
    unit: '%',
    tooltip: props.config 
      ? `Percentage of failed pings within the current window of ${props.config.max_points} pings`
      : 'Percentage of failed pings within the current window'
  },
  {
    label: 'Average Ping Time',
    value: props.stats.avg_ping_time,
    unit: 'ms',
    tooltip: 'Mean response time for successful ping requests in milliseconds'
  },
  {
    label: 'Min Ping Time',
    value: props.stats.min_ping_time,
    unit: 'ms',
    tooltip: 'Fastest response time recorded for a successful ping request'
  },
  {
    label: 'Max Ping Time',
    value: props.stats.max_ping_time,
    unit: 'ms',
    tooltip: 'Slowest response time recorded for a successful ping request'
  },
  {
    label: 'Average Outage Duration',
    value: props.stats.avg_outage_duration,
    unit: 'pings',
    tooltip: props.config 
      ? `Average duration of outages (sequences of 2+ failed pings) within the current window of ${props.config.max_points} pings`
      : 'Average duration of outages within the current window'
  },
  {
    label: 'Total Pings',
    value: props.stats.total_pings,
    unit: '',
    tooltip: 'Total number of ping requests sent during the monitoring period'
  }
]);
</script>

<style scoped>
.stats-box {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 0;
  max-width: 800px;
  width: fit-content;
}

.stats-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 1rem;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, max-content));
  gap: 1rem;
  justify-content: center;
}
</style> 