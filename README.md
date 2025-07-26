# Ping Monitor - Real-time Network Monitoring Web App

A real-time network monitoring application that continuously pings a target IP address and displays live statistics and visualizations through a web interface.

## Features

- **Real-time Network Monitoring**: Continuously pings target IP (default: 8.8.8.8)
- **Interactive Web Dashboard**: Pause/resume functionality with manual refresh
- **Dual Metrics Display**: Shows both TTL (Time To Live) and ping response times
- **Network Statistics**: Failure rates, average/min/max ping times, failure durations
- **Interactive Charts**: Plotly-based visualizations with zoom, pan, and hover tooltips
- **Smart Failure Handling**: Uses None values instead of arbitrary numbers for failed pings
- **Background Processing**: Non-blocking ping operations using threading

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The app will:
1. Start a Flask web server on `http://localhost:5000`
2. Automatically open your browser
3. Begin continuous ping monitoring
4. Display real-time charts and statistics

Press `Ctrl+C` to stop.

## Web Interface

### Controls
- **Pause/Resume**: Stop/start automatic updates while monitoring continues
- **Refresh Now**: Manually update with latest data (works even when paused)
- **Status Indicator**: Shows "LIVE" (green) or "PAUSED" (yellow)

### Charts
- **TTL Plot**: Time To Live values over time
- **Ping Time Plot**: Response times in milliseconds
- **Failure Indicators**: Red X markers show failed pings

### Statistics
- **Failure Rate**: Percentage of failed pings
- **Average/Min/Max Ping Time**: Network performance metrics
- **Average Failure Duration**: Typical length of failure periods
- **Total Pings**: Total number of ping attempts

## Configuration

Modify in `main.py`:
```python
app = create_app(target="8.8.8.8", max_points=60)
```

- `target`: IP address to monitor
- `max_points`: Number of data points to maintain

## Architecture

```
main.py (Entry Point)
    ↓
ping_monitor/ (Package)
    ├── web_app.py (Flask Application Layer)
    ├── ping_engine.py (Data Collection Layer)
    ├── statistics.py (Business Logic Layer)
    ├── plot_generator.py (Visualization Layer)
    ├── templates.py (Presentation Layer)
    └── config.py (Configuration Layer)
```

## Technical Details

- **Background Threading**: Non-blocking ping operations
- **Rolling Window**: Efficient data management with `collections.deque`
- **Thread Safety**: Proper locking for concurrent access
- **Error Handling**: Comprehensive logging and graceful recovery
- **Cross-platform**: Uses system `ping` command (macOS, Linux, Windows)

## What is TTL?

TTL (Time To Live) indicates how many network hops a packet can traverse before being discarded. Each router decrements the TTL by 1, helping identify:
- Network path changes
- Routing issues
- Different network paths to the destination 