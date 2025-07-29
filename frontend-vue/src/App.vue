<template>
  <div class="container">
    <div v-if="error && !data" class="error-message">
      <h2>Connection Error</h2>
      <p>{{ error }}</p>
      <button @click="fetchData" class="control-button">Retry</button>
    </div>

    <div v-else>
      <div class="controls">
        <button 
          :class="['control-button', { paused: isPaused }]"
          @click="togglePause"
        >
          {{ isPaused ? 'Resume' : 'Pause' }}
        </button>
        <button class="control-button" @click="fetchData">
          Refresh
        </button>
        <button class="control-button" @click="resetStatistics">
          Reset
        </button>
        <span :class="['status-indicator', isPaused ? 'status-paused' : 'status-live']">
          {{ isPaused ? 'PAUSED' : 'LIVE' }}
        </span>
      </div>

      <LoadingSpinner v-if="isLoading && !data" message="Loading network data..." />
                       <template v-else-if="data">
                   <NetworkPlot :chart-data="data.chart_data" :max-points="config?.max_points" />
                   <NetworkStats :stats="data" :config="config" />
                 </template>
      <LoadingSpinner v-else message="Initializing..." />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import NetworkPlot from './components/NetworkPlot/index.vue';
import NetworkStats from './components/NetworkStats.vue';
import LoadingSpinner from './components/LoadingSpinner.vue';
import { apiService, updateApiBaseUrl } from './services/api';
import { ERROR_MESSAGES, DEFAULT_POLLING_INTERVAL } from './constants';
import { usePolling } from './composables/usePolling';
import type { Config, ApiResponse } from './types/NetworkStats';

const config = ref<Config | null>(null);
const isPaused = ref(false);

const {
  data,
  error,
  isLoading,
  refetch: fetchData,
  setError
} = usePolling({
  fetchFn: apiService.getData,
  isPaused: computed(() => isPaused.value),
  interval: computed(() => config.value?.auto_refresh_interval ? config.value.auto_refresh_interval * 1000 : DEFAULT_POLLING_INTERVAL)
});

const fetchConfig = async () => {
  try {
    const configData = await apiService.getConfig();
    config.value = configData;
    // Update API base URL with the one from backend config
    if (configData.api_url) {
      updateApiBaseUrl(configData.api_url);
    }
  } catch (err) {
    console.error('Config fetch error:', ERROR_MESSAGES.FETCH_CONFIG, err);
  }
};

const resetStatistics = async () => {
  try {
    await apiService.resetStatistics();
    await fetchData();
  } catch (err) {
    setError(ERROR_MESSAGES.RESET_STATS);
  }
};

const togglePause = () => {
  isPaused.value = !isPaused.value;
};

onMounted(() => {
  fetchConfig();
});
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.control-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background-color: #3498db;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.control-button:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
}

.control-button.paused {
  background-color: #e74c3c;
}

.control-button.paused:hover {
  background-color: #c0392b;
}

.status-indicator {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-live {
  background-color: #27ae60;
  color: white;
}

.status-paused {
  background-color: #e74c3c;
  color: white;
}

.error-message {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.error-message h2 {
  color: #e74c3c;
  margin-bottom: 1rem;
}

.error-message p {
  color: #666;
  margin-bottom: 2rem;
}
</style> 