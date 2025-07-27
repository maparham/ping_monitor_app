# Network Ping Monitor

A simple network monitoring tool that pings a target IP and displays real-time statistics.

## Features

- Real-time ping monitoring
- Live statistics and charts
- Pause/resume functionality
- Reset statistics

## Web Interface

![Ping Monitor Dashboard](ping_monitor_app.png)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Run the application
python start.py
```

The app will open at `http://localhost:3000`

## Manual Start

```bash
# Terminal 1: Flask backend
python main.py

# Terminal 2: React frontend
cd frontend && npm start
```

## API Endpoints

- `GET /api/data` - Get current network data
- `POST /api/reset` - Reset statistics

Press `Ctrl+C` to stop. 