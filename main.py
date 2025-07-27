#!/usr/bin/env python3
"""Network Ping Monitor - Main entry point."""

import logging
from ping_monitor.web_app import create_app
from ping_monitor.config import DEFAULT_TARGET, DEFAULT_MAX_POINTS

logging.getLogger('werkzeug').setLevel(logging.ERROR)

def main():
    """Run the ping monitor API server."""
    print(f"🚀 Starting Network Monitor (target: {DEFAULT_TARGET})")
    print("Frontend: http://localhost:3000")
    print("API: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    app = create_app(target=DEFAULT_TARGET, max_points=DEFAULT_MAX_POINTS)
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == "__main__":
    main() 