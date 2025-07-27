"""Plot generator for network monitoring."""

import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Optional
from .config import DEFAULT_TARGET

class PlotGenerator:
    """Generates Plotly charts for network monitoring."""
    
    @staticmethod
    def create_plot(ttls: List[Optional[int]], ping_times: List[Optional[float]], target: str = DEFAULT_TARGET) -> go.Figure:
        """Create the Plotly figure with current data."""
        try:
            if not ttls:
                # Return empty figure if no data
                fig = go.Figure()
                fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                return fig
            
            sample_numbers = list(range(len(ttls)))
            
            # Separate successful and failed pings more efficiently
            successful_data = []
            failed_indices = []
            
            for i, (ttl, ping_time) in enumerate(zip(ttls, ping_times)):
                if ttl is not None and ping_time is not None:
                    successful_data.append((i, ttl, ping_time))
                else:
                    failed_indices.append(i)
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=(f'TTL for {target}', f'Ping Time for {target}'),
                vertical_spacing=0.2
            )
            
            # Add successful ping traces
            if successful_data:
                successful_indices, successful_ttls, successful_ping_times = zip(*successful_data)
                
                fig.add_trace(
                    go.Scatter(x=successful_indices, 
                              y=successful_ttls, mode='lines+markers', name='TTL', 
                              line=dict(color='blue', width=2), marker=dict(size=4)),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=successful_indices, 
                              y=successful_ping_times, mode='lines+markers', name='Ping Time', 
                              line=dict(color='red', width=2), marker=dict(size=4)),
                    row=2, col=1
                )
            
            # Add failure markers only if there are failures
            if failed_indices:
                max_ttl = max(successful_ttls) if successful_data else 120
                max_ping = max(successful_ping_times) if successful_data else 100
                
                fig.add_trace(
                    go.Scatter(x=failed_indices, 
                              y=[max_ttl + 2] * len(failed_indices), 
                              mode='markers', name='Failed Pings',
                              marker=dict(symbol='x', size=8, color='red')),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=failed_indices, 
                              y=[max_ping + 10] * len(failed_indices), 
                              mode='markers', name='Failed Pings',
                              marker=dict(symbol='x', size=8, color='red')),
                    row=2, col=1
                )
            
            # Update layout
            fig.update_layout(
                title=f'Network Monitoring - {time.strftime("%H:%M:%S")}',
                height=600,
                showlegend=True,
                hovermode='x unified',
                margin=dict(t=120, b=120, l=80, r=80, pad=4)
            )
            
            # Update axes
            # fig.update_xaxes(title_text="Ping Number", row=1, col=1)
            fig.update_xaxes(title_text="Ping Number", row=2, col=1)
            fig.update_yaxes(title_text="TTL", row=1, col=1)
            fig.update_yaxes(title_text="Ping Time (ms)", row=2, col=1)
            
            return fig
            
        except Exception:
            # Return empty figure on error
            fig = go.Figure()
            fig.add_annotation(text="Error creating plot", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig 