import { ref, onMounted, onUnmounted, watch, computed, type ComputedRef } from 'vue';
import { DEFAULT_POLLING_INTERVAL } from '../constants';

interface UsePollingOptions<T> {
  fetchFn: () => Promise<T>;
  isPaused?: boolean | ComputedRef<boolean>;
  interval?: number | ComputedRef<number>;
  immediate?: boolean;
}

export function usePolling<T>({ 
  fetchFn, 
  isPaused = false, 
  interval = DEFAULT_POLLING_INTERVAL,
  immediate = true 
}: UsePollingOptions<T>) {
  const data = ref<T | null>(null);
  const error = ref<string | null>(null);
  const isLoading = ref(false);
  const intervalId = ref<number | null>(null);

  // Handle computed values
  const isPausedValue = computed(() => {
    if (isPaused && typeof isPaused === 'object' && 'value' in isPaused) {
      return isPaused.value;
    }
    return isPaused as boolean;
  });

  const intervalValue = computed(() => {
    if (interval && typeof interval === 'object' && 'value' in interval) {
      return interval.value;
    }
    return interval as number;
  });

  const fetchData = async () => {
  if (isPausedValue.value) return;

  try {
    isLoading.value = true;
    // Don't clear error immediately - only clear it on successful response
    const response = await fetchFn();
    data.value = response;
    error.value = null; // Only clear error on successful response
  } catch (err) {
    // Don't set error for network timeouts or slow responses
    // This is expected behavior when backend is processing pings
    // Keep the last successful data on screen
  } finally {
    isLoading.value = false;
  }
};

  // Separate refetch function that bypasses pause check
const refetch = async () => {
  try {
    isLoading.value = true;
    const response = await fetchFn();
    data.value = response;
    error.value = null;
  } catch (err) {
    // Handle refetch errors silently
  } finally {
    isLoading.value = false;
  }
};

  const setError = (errorMessage: string) => {
    error.value = errorMessage;
  };

  const startPolling = () => {
    if (intervalId.value) {
      clearInterval(intervalId.value);
    }
    
    if (!isPausedValue.value) {
      intervalId.value = window.setInterval(fetchData, intervalValue.value);
    }
  };

  const stopPolling = () => {
    if (intervalId.value) {
      clearInterval(intervalId.value);
      intervalId.value = null;
    }
  };

  // Watch for pause state changes
  watch(isPausedValue, (newIsPaused) => {
    if (newIsPaused) {
      stopPolling();
    } else {
      startPolling();
    }
  });

  // Watch for interval changes
  watch(intervalValue, () => {
    if (!isPausedValue.value) {
      startPolling();
    }
  });

  onMounted(() => {
    if (immediate && !isPausedValue.value) {
      fetchData();
    }
    if (!isPausedValue.value) {
      startPolling();
    }
  });

  onUnmounted(() => {
    stopPolling();
  });

  return {
    data,
    error,
    isLoading,
    refetch,
    setError
  };
} 