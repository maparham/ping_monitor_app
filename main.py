#!/usr/bin/env python3
"""Network Ping Monitor - Main entry point."""

import logging
from ping_monitor.web_app import create_app
from ping_monitor.config import DEFAULT_TARGET, DEFAULT_MAX_POINTS, AUTO_REFRESH_INTERVAL, DEFAULT_HOST, DEFAULT_PORT

logging.getLogger('werkzeug').setLevel(logging.ERROR)

def main():
    """Run the ping monitor API server."""
    print(f"🚀 Starting Network Monitor (target: {DEFAULT_TARGET})")
    print("Frontend: http://localhost:3000")
    print(f"API: http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    print("Press Ctrl+C to stop\n")
    
    app = create_app(target=DEFAULT_TARGET, max_points=DEFAULT_MAX_POINTS, auto_refresh_interval=AUTO_REFRESH_INTERVAL, host=DEFAULT_HOST, port=DEFAULT_PORT)
    app.run(debug=False, host=DEFAULT_HOST, port=DEFAULT_PORT, use_reloader=False)

if __name__ == "__main__":
    main() 