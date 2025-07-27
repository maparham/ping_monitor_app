import React, { useState, useEffect, useCallback } from 'react';
import NetworkPlot from './components/NetworkPlot';
import NetworkStats from './components/NetworkStats';
import { apiService } from './services/api';
import { ApiResponse, Config } from './types/NetworkStats';
import './App.css';

function App() {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [config, setConfig] = useState<Config | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (isPaused) return;
    
    try {
      setError(null);
      const response = await apiService.getData();
      setData(response);
    } catch (err) {
      setError('Failed to fetch data');
    }
  }, [isPaused]);

  const fetchConfig = useCallback(async () => {
    try {
      const configData = await apiService.getConfig();
      setConfig(configData);
    } catch (err) {
      console.error('Failed to fetch config:', err);
    }
  }, []);

  const resetStatistics = async () => {
    try {
      await apiService.resetStatistics();
      await fetchData();
    } catch (err) {
      setError('Failed to reset statistics');
    }
  };

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  useEffect(() => {
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [fetchData]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (error) {
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

      {data ? (
        <>
          <NetworkPlot plotData={data.plot_data} />
          <NetworkStats stats={data} config={config} />
        </>
      ) : (
        <div className="loading-message">
          <strong>Loading...</strong>
        </div>
      )}
    </div>
  );
}

export default App;
