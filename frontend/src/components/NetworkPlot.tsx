import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js';
import { PlotData } from '../types/NetworkStats';

interface NetworkPlotProps {
  plotData: PlotData;
}

const NetworkPlot: React.FC<NetworkPlotProps> = ({ plotData }) => {
  const plotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (plotRef.current && plotData) {
      const layout = {
        ...plotData.layout,
        width: undefined,
        height: 600,
        autosize: true,
        margin: {
          ...plotData.layout.margin,
          t: 120,  // top margin for title
          b: 120,  // bottom margin for x-axis labels (increased)
          l: 80,   // left margin for y-axis labels
          r: 80,   // right margin
          pad: 4
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
    const handleResize = () => {
      if (plotRef.current) {
        Plotly.Plots.resize(plotRef.current);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="plot-container">
      <div ref={plotRef} id="plot" className="js-plotly-plot" />
    </div>
  );
};

export default NetworkPlot; 