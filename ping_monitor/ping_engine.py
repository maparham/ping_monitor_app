"""Ping engine for network monitoring."""

import subprocess
import re
import time
import threading
import logging
from collections import deque
from typing import Optional, Tuple, List
from .config import PING_TIMEOUT, PING_INTERVAL, DEFAULT_TARGET, DEFAULT_MAX_POINTS, DEFAULT_NUM_WINDOWS

logging.getLogger().setLevel(logging.ERROR)

class PingEngine:
    """Handles ping operations and data collection."""
    
    def __init__(self, target: str = DEFAULT_TARGET, max_points: int = DEFAULT_MAX_POINTS, num_windows: int = DEFAULT_NUM_WINDOWS):
        self.target = target
        self.max_points = max_points
        self.num_windows = num_windows
        
        self.ttls = deque(maxlen=max_points)
        self.ping_times = deque(maxlen=max_points)
        self.failed_pings = 0
        self.total_pings = 0
        
        # Track failed pings per window for sliding window calculations
        self.failed_pings_per_window = deque(maxlen=num_windows)  # Keep last N windows
        self.current_window_failed = 0
        self.current_window_total = 0
        
        self.running = False
        self.ping_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def ping_target(self) -> Tuple[Optional[int], Optional[float]]:
        """Execute ping command and extract TTL and time."""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', self.target],
                capture_output=True,
                text=True,
                timeout=PING_TIMEOUT
            )
            
            if result.returncode == 0:
                ttl_match = re.search(r'ttl=(\d+)', result.stdout)
                time_match = re.search(r'time=(\d+\.?\d*)', result.stdout)
                
                if ttl_match:
                    ttl = int(ttl_match.group(1))
                    ping_time = float(time_match.group(1)) if time_match else None
                    return ttl, ping_time
        except Exception:
            pass
        
        return None, None
    
    def _process_ping_result(self, ttl: Optional[int], ping_time: Optional[float]):
        """Process ping result and update statistics."""
        with self._lock:
            self.total_pings += 1
            self.current_window_total += 1
            
            if ttl is not None and ping_time is not None:
                self.ttls.append(ttl)
                self.ping_times.append(ping_time)
            else:
                self.ttls.append(None)
                self.ping_times.append(None)
                self.failed_pings += 1
                self.current_window_failed += 1
            
            # Check if we've completed a window
            if self.current_window_total >= self.max_points:
                # Store the failed pings count for this window
                self.failed_pings_per_window.append(self.current_window_failed)
                # Reset for next window
                self.current_window_failed = 0
                self.current_window_total = 0
    
    def _ping_loop(self):
        """Main ping loop."""
        while self.running:
            ttl, ping_time = self.ping_target()
            self._process_ping_result(ttl, ping_time)
            time.sleep(PING_INTERVAL)
    
    def start(self):
        """Start ping engine."""
        if not self.running:
            self.running = True
            self.ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
            self.ping_thread.start()
    
    def stop(self):
        """Stop ping engine."""
        self.running = False
        if self.ping_thread:
            self.ping_thread.join()
    
    def is_running(self) -> bool:
        """Check if ping engine is running."""
        return self.running
    
    def reset(self):
        """Reset all statistics."""
        with self._lock:
            self.ttls.clear()
            self.ping_times.clear()
            self.failed_pings = 0
            self.total_pings = 0
            self.failed_pings_per_window.clear()
            self.current_window_failed = 0
            self.current_window_total = 0
    
    def get_statistics(self) -> dict:
        """Get current statistics."""
        with self._lock:
            return {
                'ttls': list(self.ttls),
                'ping_times': list(self.ping_times),
                'failed_pings': self.failed_pings,
                'total_pings': self.total_pings,
                'failed_pings_per_window': list(self.failed_pings_per_window),
                'current_window_failed': self.current_window_failed,
                'current_window_total': self.current_window_total
            } 