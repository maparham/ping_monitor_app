#!/usr/bin/env python3
"""Start script for the network ping monitor."""

import subprocess
import sys
import time
import os
from ping_monitor.config import DEFAULT_HOST, DEFAULT_PORT

def main():
    """Start both Flask backend and React frontend."""
    print("🚀 Starting Network Ping Monitor")
    print("=" * 40)
    
    # Start Flask backend
    print("Starting Flask backend...")
    flask_process = subprocess.Popen([sys.executable, "main.py"])
    
    # Wait a moment for Flask to start
    time.sleep(2)
    
    # Start React frontend
    print("Starting React frontend...")
    os.chdir("frontend")
    react_process = subprocess.Popen(["npm", "start"])
    
    print("\n✅ Both services started!")
    print("Frontend: http://localhost:3000")
    print(f"API: http://{DEFAULT_HOST}:{DEFAULT_PORT}")
    print("\nPress Ctrl+C to stop both services")
    
    try:
        # Wait for processes
        flask_process.wait()
        react_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        flask_process.terminate()
        react_process.terminate()
        print("Services stopped.")

if __name__ == "__main__":
    main() 