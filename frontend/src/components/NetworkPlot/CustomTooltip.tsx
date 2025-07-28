import React from 'react';
import { FAILED_PING_MARK } from '../../constants';

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

export const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const hasFailedPing = payload.some((entry: any) => entry.value === null || entry.value === 'Failed');
    
    return (
      <div className="custom-tooltip" style={{
        backgroundColor: hasFailedPing ? '#fff5f5' : '#fff',
        border: hasFailedPing ? '1px solid #fed7d7' : '1px solid #ccc',
        padding: '10px',
        borderRadius: '4px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <p className="label" style={{ fontWeight: 'bold', marginBottom: '8px' }}>
          {`Ping #${label}`}
        </p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ 
            color: entry.value === null || entry.value === 'Failed' ? FAILED_PING_MARK.FILL_COLOR : entry.color,
            margin: '4px 0',
            fontWeight: entry.value === null || entry.value === 'Failed' ? 'bold' : 'normal'
          }}>
            {`${entry.name}: ${entry.value !== null ? entry.value : 'Failed (No Response)'}`}
          </p>
        ))}
        {hasFailedPing && (
          <p style={{ 
            fontSize: '12px', 
            color: '#718096', 
            marginTop: '8px', 
            fontStyle: 'italic' 
          }}>
            Network connection issue detected
          </p>
        )}
      </div>
    );
  }
  return null;
}; 