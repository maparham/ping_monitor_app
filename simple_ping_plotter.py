#!/usr/bin/env python3
"""
Simple real-time TTL plotter for ping to 8.8.8.8
"""

import subprocess
import re
import time
import matplotlib.pyplot as plt
import datetime

def ping_target(target="8.8.8.8"):
    """Execute ping command and extract TTL"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', target],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            ttl_match = re.search(r'ttl=(\d+)', result.stdout)
            if ttl_match:
                ttl = int(ttl_match.group(1))
                return ttl
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        pass
    
    return None

def main():
    print("Starting simple TTL plotter for 8.8.8.8...")
    print("Press Ctrl+C to stop")
    
    # Setup the plot
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots(figsize=(12, 6))
    line, = ax.plot([], [], 'b-', linewidth=2, marker='o', markersize=4)
    ax.set_xlabel('Sample Number')
    ax.set_ylabel('TTL')
    ax.set_title('Live TTL Plot for 8.8.8.8')
    ax.grid(True, alpha=0.3)
    
    # Data storage
    ttls = []
    sample_numbers = []
    
    try:
        while True:
            ttl = ping_target()
            if ttl is not None:
                ttls.append(ttl)
                sample_numbers.append(len(ttls) - 1)
                
                # Update the plot
                line.set_data(sample_numbers, ttls)
                
                # Adjust axes
                if len(ttls) > 1:
                    ax.set_xlim(0, len(ttls) - 1)
                    min_ttl = min(ttls)
                    max_ttl = max(ttls)
                    padding = max(1, (max_ttl - min_ttl) * 0.1)
                    ax.set_ylim(min_ttl - padding, max_ttl + padding)
                elif len(ttls) == 1:
                    ax.set_xlim(0, 0)
                    ax.set_ylim(ttl - 1, ttl + 1)
                
                # Redraw the plot
                fig.canvas.draw()
                fig.canvas.flush_events()
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping plotter...")
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    main() 