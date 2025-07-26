#!/usr/bin/env python3
"""
Test script to verify matplotlib plotting works
"""

import matplotlib.pyplot as plt
import time

def main():
    print("Testing matplotlib plotting with dummy data...")
    
    # Setup the plot
    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 6))
    line, = ax.plot([], [], 'b-', linewidth=2, marker='o', markersize=4)
    ax.set_xlabel('Sample Number')
    ax.set_ylabel('Value')
    ax.set_title('Test Plot')
    ax.grid(True, alpha=0.3)
    
    # Test data
    x_data = []
    y_data = []
    
    for i in range(10):
        x_data.append(i)
        y_data.append(119 + i)  # Start at 119 and increment
        
        print(f"Adding point: x={i}, y={119 + i}")
        
        # Update the plot
        line.set_data(x_data, y_data)
        
        # Adjust axes
        ax.set_xlim(0, max(x_data))
        ax.set_ylim(min(y_data) - 1, max(y_data) + 1)
        
        # Redraw
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        time.sleep(1)
    
    print("Test complete. Press Enter to close...")
    input()
    plt.ioff()
    plt.show()

if __name__ == "__main__":
    main() 