# Ping Monitor - Real-time Network Monitoring Web App

A real-time network monitoring application that continuously pings a target IP address and displays live statistics and visualizations through a web interface.

## Features

- **Real-time Network Monitoring**: Continuously pings target IP (default: 8.8.8.8)
- **Interactive Web Dashboard**: Pause/resume functionality with manual refresh
- **Reset Statistics**: One-click reset to clear all data and start fresh
- **Dual Metrics Display**: Shows both TTL (Time To Live) and ping response times
- **Advanced Network Statistics**: Failure rates, average/min/max ping times, configurable window-based averages
- **Interactive Charts**: Plotly-based visualizations with zoom, pan, and hover tooltips
- **Smart Failure Handling**: Uses None values instead of arbitrary numbers for failed pings
- **Background Processing**: Non-blocking ping operations using threading
- **Configurable Statistics**: Customizable number of windows for average calculations

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

![Ping Monitor Dashboard](ping_monitor_app.png)

The web interface provides real-time network monitoring with interactive controls and comprehensive statistics.

## Configuration

### Application Configuration
Modify in `main.py`:
```python
app = create_app(target="8.8.8.8", max_points=300)
```

## API Endpoints

- `GET /` - Main web interface
- `GET /api/data` - JSON data for AJAX requests
- `POST /api/reset` - Reset all statistics

## Technical Details

- **Background Threading**: Non-blocking ping operations
- **Rolling Window**: Efficient data management with `collections.deque`
- **Thread Safety**: Proper locking for concurrent access
- **Error Handling**: Comprehensive logging and graceful recovery
- **Cross-platform**: Uses system `ping` command (macOS, Linux, Windows)
- **Configurable Statistics**: Window-based averaging for better trend analysis
- **Reset Functionality**: Thread-safe statistics reset with re-initialization

## What is TTL?

TTL (Time To Live) indicates how many network hops a packet can traverse before being discarded. Each router decrements the TTL by 1, helping identify:
- Network path changes
- Routing issues
- Different network paths to the destination 