#!/usr/bin/env python3
"""
Main entry point for the Ping Monitor application.
"""

import webbrowser
import logging
from ping_monitor.web_app import create_app

# Suppress Flask development server logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('flask').setLevel(logging.ERROR)


def main():
    """Main function to run the ping monitor."""
    print("Starting web-based TTL plotter for 8.8.8.8...")
    print("Opening browser window...")
    print("Press Ctrl+C to stop")
    
    # Create Flask app
    app = create_app(target="8.8.8.8", max_points=60)
    
    # Open browser
    webbrowser.open('http://localhost:5000')
    
    # Start Flask app in quiet mode
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)


if __name__ == "__main__":
    main() 