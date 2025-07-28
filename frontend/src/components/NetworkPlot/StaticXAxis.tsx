import React, { useMemo } from 'react';
import { XAxis } from 'recharts';

interface StaticXAxisProps {
  maxPoints: number;
}

// Static X-axis component - never re-renders
export const StaticXAxis = React.memo<StaticXAxisProps>(({ maxPoints }) => {
  const staticXTicks = useMemo(() => {
    const ticks = [];
    const step = Math.floor(maxPoints / 6);
    for (let i = 0; i <= maxPoints; i += step) {
      ticks.push(i);
    }
    return ticks;
  }, [maxPoints]);

  return (
    <XAxis 
      dataKey="index" 
      name="Ping Number"
      tick={{ fontSize: 12 }}
      domain={[0, maxPoints]}
      allowDataOverflow={false}
      type="number"
      ticks={staticXTicks}
      allowDecimals={false}
    />
  );
}); 