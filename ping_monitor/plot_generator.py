"""
Plot Generator Module
Handles creation of Plotly charts and visualizations.
"""

import time
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Tuple, Optional
from .config import (
    DEFAULT_CHART_HEIGHT, DEFAULT_Y_PADDING_FACTOR, DEFAULT_TTL_RANGE,
    DEFAULT_PING_RANGE, DEFAULT_MAX_POINTS, DEFAULT_TARGET,
    LOG_LEVEL, LOG_FORMAT
)

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class PlotGenerator:
    """Generates Plotly charts for network monitoring."""
    
    @staticmethod
    def create_plot(ttls: List[Optional[int]], ping_times: List[Optional[float]], target: str = DEFAULT_TARGET) -> go.Figure:
        """
        Create the Plotly figure with current data.
        
        Args:
            ttls: List of TTL values (may contain None for failed pings)
            ping_times: List of ping times (may contain None for failed pings)
            target: Target IP address for display
            
        Returns:
            Plotly figure object
        """
        try:
            # Create sample numbers for the current window (always 0 to len-1)
            sample_numbers = list(range(len(ttls)))
            
            # Separate successful and failed pings for better visualization
            successful_indices = [i for i, ttl in enumerate(ttls) if ttl is not None]
            failed_indices = [i for i, ttl in enumerate(ttls) if ttl is None]
            
            # Get successful ping data
            successful_ttls = [ttls[i] for i in successful_indices]
            successful_ping_times = [ping_times[i] for i in successful_indices]
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=(f'Live TTL Plot for {target}', f'Live Ping Time Plot for {target}'),
                vertical_spacing=0.1
            )
            
            # Add successful ping traces
            if successful_ttls:
                fig.add_trace(
                    go.Scatter(x=[sample_numbers[i] for i in successful_indices], 
                              y=successful_ttls, mode='lines+markers', name='TTL', 
                              line=dict(color='blue', width=2), marker=dict(size=4)),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=[sample_numbers[i] for i in successful_indices], 
                              y=successful_ping_times, mode='lines+markers', name='Ping Time', 
                              line=dict(color='red', width=2), marker=dict(size=4)),
                    row=2, col=1
                )
            
            # Add failure markers if there are failed pings
            if failed_indices:
                # Add failure markers at the top of the chart
                max_ttl = max(successful_ttls) if successful_ttls else 120
                max_ping = max(successful_ping_times) if successful_ping_times else 100
                
                fig.add_trace(
                    go.Scatter(x=[sample_numbers[i] for i in failed_indices], 
                              y=[max_ttl + 2] * len(failed_indices), 
                              mode='markers', name='Failed Pings',
                              marker=dict(symbol='x', size=8, color='red')),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=[sample_numbers[i] for i in failed_indices], 
                              y=[max_ping + 10] * len(failed_indices), 
                              mode='markers', name='Failed Pings',
                              marker=dict(symbol='x', size=8, color='red')),
                    row=2, col=1
                )
            
            # Update layout
            fig.update_layout(
                title=f'Real-time Network Monitoring - Last updated: {time.strftime("%H:%M:%S")}',
                height=DEFAULT_CHART_HEIGHT,
                showlegend=True,
                hovermode='x unified'
            )
            
            # Update axes with dynamic range based on actual data length
            max_x = len(ttls) - 1 if ttls else 0
            fig.update_xaxes(title_text="Sample Number", row=1, col=1, range=[0, max_x])
            fig.update_xaxes(title_text="Sample Number", row=2, col=1, range=[0, max_x])
            
            # Update y-axis ranges with better error handling
            if successful_ttls and successful_ping_times:
                # TTL axis
                min_ttl = min(successful_ttls)
                max_ttl = max(successful_ttls)
                padding = max(1, (max_ttl - min_ttl) * DEFAULT_Y_PADDING_FACTOR)
                fig.update_yaxes(range=[min_ttl - padding, max_ttl + padding + 5], row=1, col=1)
                
                # Ping time axis
                min_time = min(successful_ping_times)
                max_time = max(successful_ping_times)
                padding = max(0.1, (max_time - min_time) * DEFAULT_Y_PADDING_FACTOR)
                fig.update_yaxes(range=[min_time - padding, max_time + padding + 15], row=2, col=1)
            else:
                # Default ranges when no data
                fig.update_yaxes(range=DEFAULT_TTL_RANGE, row=1, col=1)
                fig.update_yaxes(range=DEFAULT_PING_RANGE, row=2, col=1)
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating plot: {e}")
            # Return a basic figure on error
            fig = make_subplots(rows=2, cols=1, subplot_titles=('Error', 'Error'))
            fig.update_layout(title='Error generating plot')
            return fig 