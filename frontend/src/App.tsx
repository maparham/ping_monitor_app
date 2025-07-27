import React, { useState, useCallback } from 'react';
import NetworkPlot from './components/NetworkPlot';
import NetworkStats from './components/NetworkStats';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import { apiService } from './services/api';
import { ApiResponse, Config } from './types/NetworkStats';
import { ERROR_MESSAGES } from './constants';
import { usePolling } from './hooks/usePolling';
import './App.css';

function App() {
  const [config, setConfig] = useState<Config | null>(null);
  const [isPaused, setIsPaused] = useState(false);

  const {
    data,
    error,
    isLoading,
    refetch: fetchData,
    setError
  } = usePolling({
    fetchFn: apiService.getData,
    isPaused
  });

  const fetchConfig = useCallback(async () => {
    try {
      const configData = await apiService.getConfig();
      setConfig(configData);
    } catch (err) {
      console.error(ERROR_MESSAGES.FETCH_CONFIG, err);
    }
  }, []);

  const resetStatistics = async () => {
    try {
      await apiService.resetStatistics();
      await fetchData();
    } catch (err) {
      setError(ERROR_MESSAGES.RESET_STATS);
    }
  };

  React.useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  // Only show error for actual errors, not for expected network issues
  // If we have data, keep showing it even if there are network issues
  if (error && !data) {
    return (
      <div className="container">
        <div className="error-message">
          <h2>Connection Error</h2>
          <p>{error}</p>
          <button onClick={fetchData} className="control-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="container">
        <div className="controls">
          <button 
            className={`control-button ${isPaused ? 'paused' : ''}`}
            onClick={() => setIsPaused(!isPaused)}
          >
            {isPaused ? 'Resume' : 'Pause'}
          </button>
          <button className="control-button" onClick={fetchData}>
            Refresh
          </button>
          <button className="control-button" onClick={resetStatistics}>
            Reset
          </button>
          <span className={`status-indicator ${isPaused ? 'status-paused' : 'status-live'}`}>
            {isPaused ? 'PAUSED' : 'LIVE'}
          </span>
        </div>

        {isLoading && !data ? (
          <LoadingSpinner message="Loading network data..." />
        ) : data ? (
          <>
            <NetworkPlot plotData={data.plot_data} />
            <NetworkStats stats={data} config={config} />
          </>
        ) : (
          <LoadingSpinner message="Initializing..." />
        )}
      </div>
    </ErrorBoundary>
  );
}

export default App;
