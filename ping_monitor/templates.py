"""
Templates Module
Contains HTML templates for the web interface.
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Monitor</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <meta http-equiv="refresh" content="1">
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