#!/usr/bin/env python3
"""
Improved real-time TTL plotter for ping to 8.8.8.8
"""

import subprocess
import re
import time
import matplotlib.pyplot as plt
import datetime

def ping_target(target="8.8.8.8"):
    """Execute ping command and extract TTL and time"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', target],
            capture_output=True,
            text=True,
            timeout=1
        )
        
        if result.returncode == 0:
            ttl_match = re.search(r'ttl=(\d+)', result.stdout)
            time_match = re.search(r'time=(\d+\.?\d*)', result.stdout)
            
            if ttl_match:
                ttl = int(ttl_match.group(1))
                ping_time = float(time_match.group(1)) if time_match else None
                return ttl, ping_time
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        pass
    
    return None, None

def main():
    print("Starting improved TTL plotter for 8.8.8.8...")
    print("Press Ctrl+C to stop")
    
    # Setup the plot
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # TTL plot
    line1, = ax1.plot([], [], 'b-', linewidth=2, marker='o', markersize=4)
    ax1.set_xlabel('Sample Number')
    ax1.set_ylabel('TTL')
    ax1.set_title('Live TTL Plot for 8.8.8.8')
    ax1.grid(True, alpha=0.3)
    
    # Ping time plot
    line2, = ax2.plot([], [], 'r-', linewidth=2, marker='s', markersize=4)
    ax2.set_xlabel('Sample Number')
    ax2.set_ylabel('Ping Time (ms)')
    ax2.set_title('Live Ping Time Plot for 8.8.8.8')
    ax2.grid(True, alpha=0.3)
    
    # Data storage with fixed window size
    max_points = 60  # Show last 60 points (1 minute of data)
    ttls = []
    ping_times = []
    sample_numbers = []
    
    try:
        while True:
            ttl, ping_time = ping_target()
            
            if ttl is not None:
                # Successful ping
                ttls.append(ttl)
                ping_times.append(ping_time if ping_time else 0)
            else:
                # Failed ping - add -1 for both TTL and ping time
                ttls.append(-1)
                ping_times.append(700)
            
            # Maintain sliding window - remove oldest points if we exceed max_points
            if len(ttls) > max_points:
                ttls.pop(0)
                ping_times.pop(0)
            
            # Update sample numbers for the current window
            sample_numbers = list(range(len(ttls)))
            
            # Update TTL plot
            line1.set_data(sample_numbers, ttls)
            if len(ttls) > 1:
                ax1.set_xlim(0, max_points - 1)  # Fixed x-axis range
                # Include -1 in the range for failed pings
                min_ttl = min(ttls)
                max_ttl = max(ttls)
                padding = max(1, (max_ttl - min_ttl) * 0.1)
                ax1.set_ylim(min_ttl - padding, max_ttl + padding)
            elif len(ttls) == 1:
                ax1.set_xlim(0, max_points - 1)  # Fixed x-axis range
                if ttls[0] == -1:
                    ax1.set_ylim(-2, 0)
                else:
                    ax1.set_ylim(ttls[0] - 1, ttls[0] + 1)
            
            # Update ping time plot
            line2.set_data(sample_numbers, ping_times)
            if len(ping_times) > 1:
                ax2.set_xlim(0, max_points - 1)  # Fixed x-axis range
                # Include -1 in the range for failed pings
                min_time = min(ping_times)
                max_time = max(ping_times)
                padding = max(0.1, (max_time - min_time) * 0.1)
                ax2.set_ylim(min_time - padding, max_time + padding)
            elif len(ping_times) == 1:
                ax2.set_xlim(0, max_points - 1)  # Fixed x-axis range
                if ping_times[0] == -1:
                    ax2.set_ylim(-2, 0)
                else:
                    ax2.set_ylim(ping_times[0] - 1, ping_times[0] + 1)
            
            # Redraw
            fig.tight_layout()
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # Wait 1 second before next ping
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping plotter...")
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    main() 