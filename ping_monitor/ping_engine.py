"""
Ping Engine Module
Handles ping operations and data collection.
"""

import subprocess
import re
import time
import threading
import logging
from collections import deque
from typing import Optional, Tuple
from .config import (
    PING_TIMEOUT, PING_INTERVAL, DEFAULT_TARGET, DEFAULT_MAX_POINTS,
    DEFAULT_TTL, DEFAULT_PING_TIME, LOG_LEVEL, LOG_FORMAT
)

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class PingEngine:
    """Handles ping operations and data collection."""
    
    def __init__(self, target: str = DEFAULT_TARGET, max_points: int = DEFAULT_MAX_POINTS):
        """
        Initialize the ping engine.
        
        Args:
            target: IP address to ping
            max_points: Maximum number of data points to store
        """
        self.target = target
        self.max_points = max_points
        
        # Data storage - store None for failed pings
        self.ttls = deque(maxlen=max_points)
        self.ping_times = deque(maxlen=max_points)
        self.all_ping_times: list[Optional[float]] = []
        self.failed_pings = 0
        self.total_pings = 0
        self.failure_durations: list[int] = []
        self.current_failure_start: Optional[int] = None
        
        # Threading
        self.running = False
        self.ping_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()  # Thread safety
        
        # Initialize with some data
        self._initialize_data()
        logger.info(f"PingEngine initialized for target: {target}")
    
    def _initialize_data(self):
        """Initialize data structures with default values."""
        for i in range(self.max_points):
            self.ttls.append(DEFAULT_TTL)
            self.ping_times.append(DEFAULT_PING_TIME)
            self.all_ping_times.append(DEFAULT_PING_TIME)
            self.total_pings += 1
    
    def ping_target(self) -> Tuple[Optional[int], Optional[float]]:
        """
        Execute ping command and extract TTL and time.
        
        Returns:
            Tuple of (TTL, ping_time) or (None, None) if failed
        """
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
                else:
                    logger.debug(f"Could not parse TTL from ping response: {result.stdout[:100]}")
            else:
                logger.debug(f"Ping failed with return code {result.returncode}")
        except subprocess.TimeoutExpired:
            logger.debug(f"Ping timeout for {self.target}")
        except subprocess.CalledProcessError as e:
            logger.debug(f"Ping process error: {e}")
        except ValueError as e:
            logger.debug(f"Value error parsing ping response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during ping: {e}")
        
        return None, None
    
    def _process_ping_result(self, ttl: Optional[int], ping_time: Optional[float]):
        """Process a ping result and update data structures."""
        with self._lock:  # Thread safety
            self.total_pings += 1
            
            if ttl is not None and ping_time is not None:
                # Successful ping
                self.ttls.append(ttl)
                self.ping_times.append(ping_time)
                self.all_ping_times.append(ping_time)
                
                # If we were in a failure period, record the duration
                if self.current_failure_start is not None:
                    failure_duration = self.total_pings - self.current_failure_start
                    self.failure_durations.append(failure_duration)
                    self.current_failure_start = None
            else:
                # Failed ping - store None values
                self.ttls.append(None)
                self.ping_times.append(None)
                self.all_ping_times.append(None)
                self.failed_pings += 1
                
                # Start tracking failure period if not already tracking
                if self.current_failure_start is None:
                    self.current_failure_start = self.total_pings
    
    def _ping_loop(self):
        """Background thread that continuously pings and updates data."""
        logger.debug(f"Starting ping loop for {self.target}")
        while self.running:
            ttl, ping_time = self.ping_target()
            self._process_ping_result(ttl, ping_time)
            time.sleep(PING_INTERVAL)
        logger.debug("Ping loop stopped")
    
    def start(self):
        """Start the ping engine."""
        if not self.running:
            self.running = True
            self.ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
            self.ping_thread.start()
            logger.debug("Ping engine started")
    
    def stop(self):
        """Stop the ping engine."""
        if self.running:
            self.running = False
            if self.ping_thread:
                self.ping_thread.join(timeout=1)
            logger.debug("Ping engine stopped")
    
    def reset_statistics(self):
        """Reset all statistics and data to initial state."""
        with self._lock:  # Thread safety
            # Clear all data structures
            self.ttls.clear()
            self.ping_times.clear()
            self.all_ping_times.clear()
            self.failed_pings = 0
            self.total_pings = 0
            self.failure_durations.clear()
            self.current_failure_start = None
            
            # Re-initialize with default data
            self._initialize_data()
            logger.info("Statistics reset to initial state")
    
    def get_statistics(self) -> dict:
        """
        Get current statistics and data.
        
        Returns:
            Dictionary containing all statistics and current data
        """
        with self._lock:  # Thread safety
            return {
                'ttls': list(self.ttls),
                'ping_times': list(self.ping_times),
                'all_ping_times': self.all_ping_times.copy(),  # Return copy for thread safety
                'failed_pings': self.failed_pings,
                'total_pings': self.total_pings,
                'failure_durations': self.failure_durations.copy()  # Return copy for thread safety
            } 