import { useEffect, useCallback, useState, useRef } from 'react';
import { POLLING_INTERVAL } from '../constants';

interface UsePollingOptions<T> {
  fetchFn: () => Promise<T>;
  isPaused?: boolean;
  interval?: number;
  immediate?: boolean;
}

export function usePolling<T>({ 
  fetchFn, 
  isPaused = false, 
  interval = POLLING_INTERVAL,
  immediate = true 
}: UsePollingOptions<T>) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const isPausedRef = useRef(isPaused);

  // Keep the ref in sync with the prop
  useEffect(() => {
    isPausedRef.current = isPaused;
  }, [isPaused]);

  const fetchData = useCallback(async () => {
    if (isPausedRef.current) return;
    
    try {
      setIsLoading(true);
      // Don't clear error immediately - only clear it on successful response
      const response = await fetchFn();
      setData(response);
      setError(null); // Only clear error on successful response
    } catch (err) {
      // Don't set error for network timeouts or slow responses
      // This is expected behavior when backend is processing pings
      console.log('Backend request failed or needs more time to process');
      // Keep the last successful data on screen
    } finally {
      setIsLoading(false);
    }
  }, [fetchFn]);

  // Separate refetch function that bypasses pause check
  const refetch = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetchFn();
      setData(response);
      setError(null);
    } catch (err) {
      console.log('Backend request failed or needs more time to process');
    } finally {
      setIsLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    if (immediate && !isPaused) {
      fetchData();
    }
  }, [fetchData, immediate, isPaused]);

  useEffect(() => {
    if (isPaused) {
      return; // Don't set up interval when paused
    }
    
    const intervalId = setInterval(fetchData, interval);
    return () => clearInterval(intervalId);
  }, [fetchData, interval, isPaused]);

  return {
    data,
    error,
    isLoading,
    refetch,
    setError
  };
} 