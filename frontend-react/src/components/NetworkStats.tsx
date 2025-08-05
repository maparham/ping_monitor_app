import React, { useMemo } from 'react';
import StatItem from './StatItem';
import type { NetworkStats as NetworkStatsType, Config } from '../types/NetworkStats';

interface NetworkStatsProps {
  stats: NetworkStatsType;
  config: Config | null;
}

const NetworkStats: React.FC<NetworkStatsProps> = ({ stats, config }) => {
  const statItems = useMemo(() => [
    {
      label: 'Failure Rate',
      value: stats.failure_rate,
      unit: '%',
      tooltip: config 
        ? `Percentage of failed pings within the current window of ${config.max_points} pings`
        : 'Percentage of failed pings within the current window'
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
      label: 'Average Outage Duration',
      value: stats.avg_outage_duration,
      unit: 'pings',
      tooltip: config 
        ? `Average duration of outages (sequences of 2+ failed pings) within the current window of ${config.max_points} pings`
        : 'Average duration of outages within the current window'
    },
    {
      label: 'Total Pings',
      value: stats.total_pings,
      unit: '',
      tooltip: 'Total number of ping requests sent during the monitoring period'
    }
  ], [stats, config]);

  return (
    <div className="stats-box">
      <div className="stats-title">Network Statistics</div>
      <div className="stats-grid">
        {statItems.map((item, index) => (
          <StatItem
            key={`${item.label}-${index}`}
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