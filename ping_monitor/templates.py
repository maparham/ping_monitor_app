"""
Templates Module
Contains HTML templates for the web interface.
"""

import time

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Monitor</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
        .controls {
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        .control-button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 0 10px;
            transition: background-color 0.3s;
        }
        .control-button:hover {
            background-color: #0056b3;
        }
        .control-button.paused {
            background-color: #dc3545;
        }
        .control-button.paused:hover {
            background-color: #c82333;
        }
        .status-indicator {
            display: inline-block;
            margin-left: 15px;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 14px;
            font-weight: bold;
        }
        .status-live {
            background-color: #28a745;
            color: white;
        }
        .status-paused {
            background-color: #ffc107;
            color: #212529;
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
        .last-updated {
            text-align: center;
            margin-top: 10px;
            color: #6c757d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="controls">
            <button id="pauseButton" class="control-button" onclick="togglePause()">Pause</button>
            <button class="control-button" onclick="manualRefresh()">Refresh Now</button>
            <span id="statusIndicator" class="status-indicator status-live">LIVE</span>
        </div>
        
        <div id="plot"></div>
        
        <div class="stats-box">
            <div class="stats-title">Network Statistics</div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Failure Rate</div>
                    <div class="stat-value" id="failure-rate">{{ "%.1f"|format(failure_rate) }}<span class="stat-unit">%</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Average Ping Time</div>
                    <div class="stat-value" id="avg-ping-time">{{ "%.1f"|format(avg_ping_time) }}<span class="stat-unit">ms</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Min Ping Time</div>
                    <div class="stat-value" id="min-ping-time">{{ "%.1f"|format(min_ping_time) }}<span class="stat-unit">ms</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Max Ping Time</div>
                    <div class="stat-value" id="max-ping-time">{{ "%.1f"|format(max_ping_time) }}<span class="stat-unit">ms</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Avg Failure Duration</div>
                    <div class="stat-value" id="avg-failure-duration">{{ "%.1f"|format(avg_failure_duration) }}<span class="stat-unit">s</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Total Pings</div>
                    <div class="stat-value" id="total-pings">{{ total_pings }}<span class="stat-unit"></span></div>
                </div>
            </div>
        </div>
        
        <div class="last-updated" id="lastUpdated">
            Last updated: <span id="timestamp">{{ time.strftime('%H:%M:%S') }}</span>
        </div>
    </div>
    
    <script>
        let isPaused = false;
        let updateInterval;
        let currentPlotData = {{ plot_json | safe }};
        
        // Initialize the plot
        Plotly.newPlot('plot', currentPlotData.data, currentPlotData.layout);
        
        // Start auto-refresh
        startAutoRefresh();
        
        function togglePause() {
            const button = document.getElementById('pauseButton');
            const statusIndicator = document.getElementById('statusIndicator');
            
            if (isPaused) {
                // Resume
                isPaused = false;
                button.textContent = 'Pause';
                button.classList.remove('paused');
                statusIndicator.textContent = 'LIVE';
                statusIndicator.className = 'status-indicator status-live';
                startAutoRefresh();
            } else {
                // Pause
                isPaused = true;
                button.textContent = 'Resume';
                button.classList.add('paused');
                statusIndicator.textContent = 'PAUSED';
                statusIndicator.className = 'status-indicator status-paused';
                stopAutoRefresh();
            }
        }
        
        function startAutoRefresh() {
            updateInterval = setInterval(refreshData, 1000);
        }
        
        function stopAutoRefresh() {
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
        }
        
        function refreshData() {
            if (isPaused) return;
            
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    // Update plot
                    Plotly.react('plot', data.plot_data.data, data.plot_data.layout);
                    
                    // Update statistics
                    document.getElementById('failure-rate').innerHTML = data.failure_rate.toFixed(1) + '<span class="stat-unit">%</span>';
                    document.getElementById('avg-ping-time').innerHTML = data.avg_ping_time.toFixed(1) + '<span class="stat-unit">ms</span>';
                    document.getElementById('min-ping-time').innerHTML = data.min_ping_time.toFixed(1) + '<span class="stat-unit">ms</span>';
                    document.getElementById('max-ping-time').innerHTML = data.max_ping_time.toFixed(1) + '<span class="stat-unit">ms</span>';
                    document.getElementById('avg-failure-duration').innerHTML = data.avg_failure_duration.toFixed(1) + '<span class="stat-unit">s</span>';
                    document.getElementById('total-pings').innerHTML = data.total_pings + '<span class="stat-unit"></span>';
                    
                    // Update timestamp
                    const now = new Date();
                    document.getElementById('timestamp').textContent = now.toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        }
        
        // Manual refresh function - works even when paused
        function manualRefresh() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    // Update plot
                    Plotly.react('plot', data.plot_data.data, data.plot_data.layout);
                    
                    // Update statistics
                    document.getElementById('failure-rate').innerHTML = data.failure_rate.toFixed(1) + '<span class="stat-unit">%</span>';
                    document.getElementById('avg-ping-time').innerHTML = data.avg_ping_time.toFixed(1) + '<span class="stat-unit">ms</span>';
                    document.getElementById('min-ping-time').innerHTML = data.min_ping_time.toFixed(1) + '<span class="stat-unit">ms</span>';
                    document.getElementById('max-ping-time').innerHTML = data.max_ping_time.toFixed(1) + '<span class="stat-unit">ms</span>';
                    document.getElementById('avg-failure-duration').innerHTML = data.avg_failure_duration.toFixed(1) + '<span class="stat-unit">s</span>';
                    document.getElementById('total-pings').innerHTML = data.total_pings + '<span class="stat-unit"></span>';
                    
                    // Update timestamp
                    const now = new Date();
                    document.getElementById('timestamp').textContent = now.toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        }
    </script>
</body>
</html>
""" 