#!/usr/bin/env python3
"""
Web-based real-time TTL plotter for ping to 8.8.8.8 using Flask and Plotly
"""

import subprocess
import re
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.utils
import json
from collections import deque
from flask import Flask, render_template_string
import threading
import webbrowser

app = Flask(__name__)

# Global data storage
max_points = 60
ttls = deque(maxlen=max_points)
ping_times = deque(maxlen=max_points)
all_ping_times = []  # Store all ping times for statistics
failed_pings = 0     # Count of failed pings
total_pings = 0      # Total number of pings
failure_durations = []  # Store duration of failure periods in seconds
current_failure_start = None  # Track when current failure started

# Initialize with some data
for i in range(60):
    ttls.append(119)
    ping_times.append(10)
    all_ping_times.append(10)
    total_pings += 1

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

def calculate_statistics():
    """Calculate statistics from the data"""
    if total_pings == 0:
        return 0, 0, 0, 0, 0
    
    # Calculate failure rate
    failure_rate = (failed_pings / total_pings) * 100
    
    # Calculate average ping time (excluding failed pings)
    successful_pings = [t for t in all_ping_times if t != 700]  # 700 is our failure indicator
    avg_ping_time = sum(successful_pings) / len(successful_pings) if successful_pings else 0
    
    # Calculate min and max ping times
    min_ping_time = min(successful_pings) if successful_pings else 0
    max_ping_time = max(successful_pings) if successful_pings else 0
    
    # Calculate average failure duration
    avg_failure_duration = sum(failure_durations) / len(failure_durations) if failure_durations else 0
    
    return failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failure_duration

def create_plot():
    """Create the Plotly figure with current data"""
    # Create sample numbers for the current window (always 0 to len-1)
    sample_numbers = list(range(len(ttls)))
    
    # Calculate statistics
    failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failure_duration = calculate_statistics()
    
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
    
    # Update layout
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

# HTML template with auto-refresh
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Monitor</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <meta http-equiv="refresh" content="2">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stats-box {
            background-color: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            text-align: center;
        }
        .stats-title {
            font-size: 18px;
            font-weight: bold;
            color: #495057;
            margin-bottom: 15px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-item {
            background-color: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stat-label {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #212529;
        }
        .stat-unit {
            font-size: 14px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="plot"></div>
        
        <div class="stats-box">
            <div class="stats-title">Network Statistics</div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Failure Rate</div>
                    <div class="stat-value">{{ "%.1f"|format(failure_rate) }}<span class="stat-unit">%</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Average Ping Time</div>
                    <div class="stat-value">{{ "%.1f"|format(avg_ping_time) }}<span class="stat-unit">ms</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Min Ping Time</div>
                    <div class="stat-value">{{ "%.1f"|format(min_ping_time) }}<span class="stat-unit">ms</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Max Ping Time</div>
                    <div class="stat-value">{{ "%.1f"|format(max_ping_time) }}<span class="stat-unit">ms</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Avg Failure Duration</div>
                    <div class="stat-value">{{ "%.1f"|format(avg_failure_duration) }}<span class="stat-unit">s</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Pings</div>
                    <div class="stat-value">{{ total_pings }}<span class="stat-unit"></span></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        var data = {{ plot_json | safe }};
        Plotly.newPlot('plot', data.data, data.layout);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main page with the plot"""
    fig = create_plot()
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Calculate statistics for the template
    failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failure_duration = calculate_statistics()
    
    return render_template_string(HTML_TEMPLATE, 
                                plot_json=plot_json,
                                failure_rate=failure_rate,
                                avg_ping_time=avg_ping_time,
                                min_ping_time=min_ping_time,
                                max_ping_time=max_ping_time,
                                avg_failure_duration=avg_failure_duration,
                                total_pings=total_pings)

def ping_loop():
    """Background thread that continuously pings and updates data"""
    global failed_pings, total_pings, all_ping_times, current_failure_start, failure_durations
    
    while True:
        ttl, ping_time = ping_target()
        total_pings += 1
        
        if ttl is not None:
            # Successful ping
            ttls.append(ttl)
            ping_times.append(ping_time if ping_time else 0)
            all_ping_times.append(ping_time if ping_time else 0)
            
            # If we were in a failure period, record the duration
            if current_failure_start is not None:
                failure_duration = total_pings - current_failure_start
                failure_durations.append(failure_duration)
                current_failure_start = None
        else:
            # Failed ping - add -1 for TTL and 700 for ping time
            ttls.append(-1)
            ping_times.append(700)
            all_ping_times.append(700)
            failed_pings += 1
            
            # Start tracking failure period if not already tracking
            if current_failure_start is None:
                current_failure_start = total_pings
        
        time.sleep(1)

def main():
    print("Starting web-based TTL plotter for 8.8.8.8...")
    print("Opening browser window...")
    print("Press Ctrl+C to stop")
    
    # Start the ping loop in a background thread
    ping_thread = threading.Thread(target=ping_loop, daemon=True)
    ping_thread.start()
    
    # Open browser
    webbrowser.open('http://localhost:5000')
    
    # Start Flask app
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 