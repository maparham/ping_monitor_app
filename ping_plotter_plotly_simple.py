#!/usr/bin/env python3
"""
Simple interactive TTL plotter for ping to 8.8.8.8 using Plotly with auto-refresh
"""

import subprocess
import re
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
from collections import deque
import os

def ping_target(target="8.8.8.8"):
    """Execute ping command and extract TTL and time"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', target],
            capture_output=True,
            text=True,
            timeout=1
        )
        
        if result.returncode == 0:
            ttl_match = re.search(r'ttl=(\d+)', result.stdout)
            time_match = re.search(r'time=(\d+\.?\d*)', result.stdout)
            
            if ttl_match:
                ttl = int(ttl_match.group(1))
                ping_time = float(time_match.group(1)) if time_match else None
                return ttl, ping_time
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        pass
    
    return None, None

def create_plot(ttls, ping_times):
    """Create the Plotly figure with current data"""
    sample_numbers = list(range(len(ttls)))
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Live TTL Plot for 8.8.8.8', 'Live Ping Time Plot for 8.8.8.8'),
        vertical_spacing=0.1
    )
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=sample_numbers, y=list(ttls), mode='lines+markers', name='TTL', 
                  line=dict(color='blue', width=2), marker=dict(size=4)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=sample_numbers, y=list(ping_times), mode='lines+markers', name='Ping Time', 
                  line=dict(color='red', width=2), marker=dict(size=4)),
        row=2, col=1
    )
    
    # Update layout with auto-refresh
    fig.update_layout(
        title=f'Real-time Network Monitoring - Last updated: {time.strftime("%H:%M:%S")}',
        height=800,
        showlegend=True,
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Sample Number", row=1, col=1, range=[0, 59])
    fig.update_xaxes(title_text="Sample Number", row=2, col=1, range=[0, 59])
    
    # Update y-axis ranges
    if len(ttls) > 0:
        min_ttl = min(ttls)
        max_ttl = max(ttls)
        padding = max(1, (max_ttl - min_ttl) * 0.1)
        fig.update_yaxes(range=[min_ttl - padding, max_ttl + padding], row=1, col=1)
        
        min_time = min(ping_times)
        max_time = max(ping_times)
        padding = max(0.1, (max_time - min_time) * 0.1)
        fig.update_yaxes(range=[min_time - padding, max_time + padding], row=2, col=1)
    else:
        fig.update_yaxes(range=[115, 125], row=1, col=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)
    
    return fig

def main():
    print("Starting interactive TTL plotter for 8.8.8.8...")
    print("Opening browser window...")
    print("Press Ctrl+C to stop")
    
    # Data storage with fixed window size
    max_points = 60  # Show last 60 points (1 minute of data)
    ttls = deque(maxlen=max_points)
    ping_times = deque(maxlen=max_points)
    
    # Initialize with some data
    for i in range(60):
        ttls.append(119)
        ping_times.append(10)
    
    # Create initial plot and save to HTML
    fig = create_plot(ttls, ping_times)
    html_file = "network_monitor.html"
    fig.write_html(html_file, auto_open=True)
    
    try:
        while True:
            ttl, ping_time = ping_target()
            
            if ttl is not None:
                # Successful ping
                ttls.append(ttl)
                ping_times.append(ping_time if ping_time else 0)
            else:
                # Failed ping - add -1 for TTL and 700 for ping time
                ttls.append(-1)
                ping_times.append(700)
            
            # Create updated plot and save to HTML
            fig = create_plot(ttls, ping_times)
            fig.write_html(html_file, auto_open=False)
            
            # Wait 1 second before next ping
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping plotter...")
        # Clean up HTML file
        if os.path.exists(html_file):
            os.remove(html_file)

if __name__ == "__main__":
    main() 