"""Ping engine for network monitoring."""

import subprocess
import re
import time
import threading
import logging
from collections import deque
from typing import Optional, Tuple, List

try:
    from .config import PING_TIMEOUT, PING_INTERVAL, DEFAULT_TARGET, DEFAULT_MAX_POINTS
except ImportError:
    from config import PING_TIMEOUT, PING_INTERVAL, DEFAULT_TARGET, DEFAULT_MAX_POINTS

logging.getLogger().setLevel(logging.ERROR)

class PingEngine:
    """Handles ping operations and data collection with sliding window outage detection."""

    def __init__(self, target: str = DEFAULT_TARGET, max_points: int = DEFAULT_MAX_POINTS):
        # Configuration
        self.target = target
        self.max_points = max_points
        
        # Data storage (auto-limited by deque maxlen)
        self.ttls = deque(maxlen=max_points)
        self.ping_times = deque(maxlen=max_points)
        
        # Overall statistics
        self.failed_pings = 0
        self.total_pings = 0
        
        # Outage detection state
        self.consecutive_failures = 0
        self.outage_start_index: Optional[int] = None
        
        # Historical outage tracking - stores (start_index, duration) tuples
        self.outage_history: List[Tuple[int, int]] = []
        
        # Threading controls
        self.running = False
        self.ping_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def ping_target(self) -> Tuple[Optional[int], Optional[float]]:
        """Execute ping command and extract TTL and time."""
        try:
            # Execute single ping command with timeout
            result = subprocess.run(
                ['ping', '-c', '1', self.target],
                capture_output=True,
                text=True,
                timeout=PING_TIMEOUT
            )
            
            # Parse successful ping output
            if result.returncode == 0:
                ttl_match = re.search(r'ttl=(\d+)', result.stdout)
                time_match = re.search(r'time=(\d+\.?\d*)', result.stdout)
                
                ttl = int(ttl_match.group(1)) if ttl_match else None
                ping_time = float(time_match.group(1)) if time_match else None
                return ttl, ping_time
                
        except Exception:
            # Any exception means ping failed
            pass
            
        return None, None

    def _update_outage_history(self) -> None:
        """Decrement start indices of all outages and remove outdated ones."""
        updated_outages = []
        for start_idx, duration in self.outage_history:
            # Decrement start index as window slides
            new_start_idx = start_idx - 1
            
            # Keep outages that are still within the window (start index >= 0)
            if new_start_idx >= 0:
                updated_outages.append((new_start_idx, duration))
                
        self.outage_history = updated_outages

    def _record_outage(self, start_index: int, duration: int) -> None:
        """Record a valid outage (2+ consecutive failures) in the history."""
        if duration >= 2:
            self.outage_history.append((start_index, duration))

    def _handle_successful_ping(self, ttl: int, ping_time: float) -> None:
        """Process a successful ping result and handle outage ending."""
        # Store successful ping data
        self.ttls.append(ttl)
        self.ping_times.append(ping_time)
        
        # Check if we're ending an outage (2+ consecutive failures)
        if self.consecutive_failures >= 2:
            # Use the recorded start index from when the outage began
            self._record_outage(self.outage_start_index, self.consecutive_failures)
        
        # Reset outage tracking since ping succeeded
        self.consecutive_failures = 0
        self.outage_start_index = None

    def _handle_failed_ping(self) -> None:
        """Process a failed ping result and track consecutive failures."""
        # Store failed ping data
        self.ttls.append(None)
        self.ping_times.append(None)
        
        # Update failure counters
        self.failed_pings += 1
        self.consecutive_failures += 1
        
        # Mark outage start when we hit 2 consecutive failures
        if self.consecutive_failures == 2:
            # Outage enters the window from the right boundary
            self.outage_start_index = self.max_points - 1

    def _process_ping_result(self, ttl: Optional[int], ping_time: Optional[float]) -> None:
        """Process ping result and update all statistics and outage tracking."""
        with self._lock:
            # Update basic counters
            self.total_pings += 1
            
            # Update outage history indices on every ping
            self._update_outage_history()
            
            # Process ping result
            if ttl is not None and ping_time is not None: # successful ping
                self._handle_successful_ping(ttl, ping_time)
            else: # failed ping
                self._handle_failed_ping()

    def _ping_loop(self) -> None:
        """Main ping execution loop that runs in background thread."""
        while self.running:
            # Execute single ping and process result
            ttl, ping_time = self.ping_target()
            self._process_ping_result(ttl, ping_time)
            
            # Wait before next ping
            time.sleep(PING_INTERVAL)

    def start(self) -> None:
        """Start the ping engine in a background thread."""
        if not self.running:
            self.running = True
            self.ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
            self.ping_thread.start()

    def stop(self) -> None:
        """Stop the ping engine and wait for thread to finish."""
        self.running = False
        if self.ping_thread and self.ping_thread.is_alive():
            self.ping_thread.join()

    def is_running(self) -> bool:
        """Check if ping engine is currently running."""
        return self.running

    def reset(self) -> None:
        """Reset all statistics and outage tracking to initial state."""
        with self._lock:
            # Clear data storage
            self.ttls.clear()
            self.ping_times.clear()
            
            # Reset overall counters
            self.failed_pings = 0
            self.total_pings = 0
            
            # Reset outage detection
            self.outage_history.clear()
            self.consecutive_failures = 0
            self.outage_start_index = None

    def get_statistics(self) -> dict:
        """Get current statistics snapshot with thread-safe access."""
        with self._lock:
            # Calculate sliding window statistics
            window_pings = len(self.ping_times)
            window_failed_pings = sum(1 for ping_time in self.ping_times if ping_time is None)
            
            # Calculate failure rate within the sliding window
            failure_rate = (window_failed_pings / window_pings * 100) if window_pings > 0 else 0.0
            
            return {
                'ttls': list(self.ttls),
                'ping_times': list(self.ping_times),
                'failed_pings': self.failed_pings,
                'total_pings': self.total_pings,
                'failure_rate': failure_rate,
                'outage_history': [duration for _, duration in self.outage_history],
                'consecutive_failures': self.consecutive_failures,
                'outage_start_index': self.outage_start_index
            } 