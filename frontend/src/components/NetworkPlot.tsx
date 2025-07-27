import React, { useEffect, useRef, useCallback } from 'react';
import Plotly from 'plotly.js';
import { PlotData } from '../types/NetworkStats';
import { PLOT_HEIGHT, PLOT_MARGIN, RESIZE_DEBOUNCE_MS } from '../constants';

interface NetworkPlotProps {
  plotData: PlotData;
}

const NetworkPlot: React.FC<NetworkPlotProps> = ({ plotData }) => {
  const plotRef = useRef<HTMLDivElement>(null);
  const resizeTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

  const handleResize = useCallback(() => {
    if (resizeTimeoutRef.current) {
      clearTimeout(resizeTimeoutRef.current);
    }
    
    resizeTimeoutRef.current = setTimeout(() => {
      if (plotRef.current) {
        Plotly.Plots.resize(plotRef.current);
      }
    }, RESIZE_DEBOUNCE_MS);
  }, []);

  useEffect(() => {
    if (plotRef.current && plotData) {
      const layout = {
        ...plotData.layout,
        width: undefined,
        height: PLOT_HEIGHT,
        autosize: true,
        margin: {
          ...plotData.layout.margin,
          ...PLOT_MARGIN
        }
      };
      
      Plotly.react(plotRef.current, plotData.data, layout, {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d']
      });
    }
  }, [plotData]);

  useEffect(() => {
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }
    };
  }, [handleResize]);

  return (
    <div className="plot-container">
      <div ref={plotRef} id="plot" className="js-plotly-plot" />
    </div>
  );
};

export default NetworkPlot; 