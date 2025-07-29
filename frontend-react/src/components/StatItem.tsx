import React from 'react';

interface StatItemProps {
  label: string;
  value: number | null;
  unit: string;
  tooltip?: string;
}

const StatItem: React.FC<StatItemProps> = ({ label, value, unit, tooltip }) => {
  const formatValue = (val: number | null): string => {
    if (val === undefined || val === null) return 'N/A';
    if (val === Infinity) return '∞';
    return `${val.toFixed(1)}`;
  };

  return (
    <div className="stat-item">
      <div className="stat-header">
        <div className="stat-label">{label}</div>
        {tooltip && (
          <div className="tooltip-container">
            <span className="tooltip-icon">ⓘ</span>
            <div className="tooltip-text">{tooltip}</div>
          </div>
        )}
      </div>
      <div className="stat-value">
        {formatValue(value)}<span className="stat-unit">{unit}</span>
      </div>
    </div>
  );
};

export default StatItem; 