import { useEffect, useCallback, useState } from 'react';
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

  const fetchData = useCallback(async () => {
    if (isPaused) return;
    
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetchFn();
      setData(response);
    } catch (err) {
      setError('Failed to fetch data');
    } finally {
      setIsLoading(false);
    }
  }, [fetchFn, isPaused]);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [fetchData, immediate]);

  useEffect(() => {
    const intervalId = setInterval(fetchData, interval);
    return () => clearInterval(intervalId);
  }, [fetchData, interval]);

  return {
    data,
    error,
    isLoading,
    refetch: fetchData,
    setError
  };
} 