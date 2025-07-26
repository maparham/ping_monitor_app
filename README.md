# Ping Monitor - Real-time Network Monitoring Web App

A real-time network monitoring application that continuously pings a target IP address and displays live statistics and visualizations through a web interface.

## Features

- **Real-time Network Monitoring**: Continuously pings target IP (default: 8.8.8.8)
- **Live Web Dashboard**: Interactive web interface with auto-refresh
- **Dual Metrics Display**: Shows both TTL (Time To Live) and ping response times
- **Network Statistics**: Calculates failure rates, average/min/max ping times, and failure durations
- **Interactive Charts**: Plotly-based visualizations with zoom, pan, and hover tooltips
- **Rolling Data Window**: Maintains last 60 data points by default
- **Background Processing**: Non-blocking ping operations using threading
- **Smart Failure Handling**: Uses None values instead of arbitrary numbers for failed pings

## Architecture

The application follows a modular design with clear separation of concerns:

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

### Core Components

- **PingEngine**: Background thread that executes ping commands and stores data
- **StatisticsCalculator**: Processes raw data into meaningful network metrics
- **PlotGenerator**: Creates interactive Plotly charts for data visualization
- **WebApp**: Flask application that serves the web interface
- **Templates**: HTML template with embedded JavaScript for real-time updates
- **Config**: Centralized configuration management

## Requirements

- Python 3.6+
- Flask
- Plotly
- Network connectivity to target IP

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

The application will:
1. Start a Flask web server on `http://localhost:5000`
2. Automatically open your default web browser
3. Begin continuous ping monitoring in the background
4. Display real-time charts and statistics
5. Auto-refresh the page every second

Press `Ctrl+C` to stop the application.

## Web Interface

The web dashboard displays:

### Charts
- **TTL Plot**: Shows Time To Live values over time
- **Ping Time Plot**: Shows response times in milliseconds
- **Failure Indicators**: Failed pings are shown as red X markers at the top of charts

### Statistics Panel
- **Failure Rate**: Percentage of failed pings
- **Average Ping Time**: Mean response time (excluding failures)
- **Min/Max Ping Time**: Network performance bounds
- **Average Failure Duration**: Typical length of failure periods
- **Total Pings**: Total number of ping attempts

## Configuration

You can modify the target IP and data window size in `main.py`:

```python
app = create_app(target="8.8.8.8", max_points=60)
```

- `target`: IP address to monitor (default: 8.8.8.8)
- `max_points`: Number of data points to maintain (default: 60)

## What is TTL?

TTL (Time To Live) is a value in the IP header that indicates how many network hops a packet can traverse before being discarded. Each router that forwards the packet decrements the TTL by 1. The TTL value can help identify:

- Network path changes
- Routing issues
- Different network paths to the destination

## Technical Details

- **Background Threading**: Ping operations run in a separate thread to avoid blocking the web server
- **Rolling Window**: Uses `collections.deque` with `maxlen` for efficient data management
- **Failure Tracking**: Monitors failed pings and calculates failure durations
- **Real-time Updates**: Page auto-refreshes every second for live data
- **Cross-platform**: Uses system `ping` command, works on macOS, Linux, and Windows
- **Thread Safety**: Proper locking mechanisms for concurrent data access
- **Error Handling**: Comprehensive logging and graceful error recovery
- **Smart Data Handling**: Uses None values for failed pings instead of arbitrary numbers

## Notes

- The application uses the system's `ping` command
- Failed pings are represented as None values and shown as red X markers in charts
- The web interface automatically refreshes every second
- All data is stored in memory and resets when the application restarts
- Comprehensive logging is available for debugging and monitoring 