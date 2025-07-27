import React from 'react';
import StatItem from './StatItem';
import type { NetworkStats as NetworkStatsType, Config } from '../types/NetworkStats';

interface NetworkStatsProps {
  stats: NetworkStatsType;
  config: Config | null;
}

const NetworkStats: React.FC<NetworkStatsProps> = ({ stats, config }) => {
  const statItems = [
    {
      label: 'Failure Rate',
      value: stats.failure_rate,
      unit: '%',
      tooltip: 'Percentage of ping requests that failed to reach the target host'
    },
    {
      label: 'Average Ping Time',
      value: stats.avg_ping_time,
      unit: 'ms',
      tooltip: 'Mean response time for successful ping requests in milliseconds'
    },
    {
      label: 'Min Ping Time',
      value: stats.min_ping_time,
      unit: 'ms',
      tooltip: 'Fastest response time recorded for a successful ping request'
    },
    {
      label: 'Max Ping Time',
      value: stats.max_ping_time,
      unit: 'ms',
      tooltip: 'Slowest response time recorded for a successful ping request'
    },
    {
      label: 'Average Failed Pings',
      value: stats.avg_failed_pings,
      unit: '',
      tooltip: config 
        ? `Average number of failed pings over the last ${config.num_windows} windows of ${config.max_points} pings`
        : 'Average number of failed pings'
    },
    {
      label: 'Total Pings',
      value: stats.total_pings,
      unit: '',
      tooltip: 'Total number of ping requests sent during the monitoring period'
    }
  ];

  return (
    <div className="stats-box">
      <div className="stats-title">Network Statistics</div>
      <div className="stats-grid">
        {statItems.map((item, index) => (
          <StatItem
            key={index}
            label={item.label}
            value={item.value}
            unit={item.unit}
            tooltip={item.tooltip}
          />
        ))}
      </div>
    </div>
  );
};

export default NetworkStats; 