import React from 'react';

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

export const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip" style={{
        backgroundColor: '#fff',
        border: '1px solid #ccc',
        padding: '10px',
        borderRadius: '4px'
      }}>
        <p className="label">{`Ping #${label}`}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }}>
            {`${entry.name}: ${entry.value !== null ? entry.value : 'Failed'}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
}; 