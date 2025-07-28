import React from 'react';
import { FAILED_PING_MARK } from '../../constants';

interface FailedPingShapeProps {
  cx: number;
  cy: number;
  payload: any;
  dataKey: string;
}

export const FailedPingShape: React.FC<FailedPingShapeProps> = ({ cx, cy, payload, dataKey }) => {
  if (!payload || payload[dataKey] === undefined) {
    return <g />; // Return empty group instead of null
  }
  
  return (
    <g>
      <line
        x1={cx - FAILED_PING_MARK.RADIUS}
        y1={cy - FAILED_PING_MARK.RADIUS}
        x2={cx + FAILED_PING_MARK.RADIUS}
        y2={cy + FAILED_PING_MARK.RADIUS}
        stroke={FAILED_PING_MARK.STROKE_COLOR}
        strokeWidth={FAILED_PING_MARK.STROKE_WIDTH}
      />
      <line
        x1={cx + FAILED_PING_MARK.RADIUS}
        y1={cy - FAILED_PING_MARK.RADIUS}
        x2={cx - FAILED_PING_MARK.RADIUS}
        y2={cy + FAILED_PING_MARK.RADIUS}
        stroke={FAILED_PING_MARK.STROKE_COLOR}
        strokeWidth={FAILED_PING_MARK.STROKE_WIDTH}
      />
    </g>
  );
}; 