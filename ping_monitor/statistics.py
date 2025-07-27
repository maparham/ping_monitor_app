"""
Statistics Module
Handles calculation of network statistics.
"""

import logging
from typing import Dict, Tuple, List, Optional
from .config import LOG_LEVEL, LOG_FORMAT, DEFAULT_MAX_POINTS, DEFAULT_NUM_WINDOWS

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class StatisticsCalculator:
    """Calculates network statistics from ping data."""
    
    @staticmethod
    def calculate_statistics(stats_data: Dict) -> Tuple[float, float, float, float, float]:
        """
        Calculate statistics from ping data.
        
        Args:
            stats_data: Dictionary containing ping statistics
            
        Returns:
            Tuple of (failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings)
        """
        try:
            total_pings = stats_data.get('total_pings', 0)
            failed_pings = stats_data.get('failed_pings', 0)
            all_ping_times: List[Optional[float]] = stats_data.get('all_ping_times', [])
            
            if total_pings == 0:
                return 0.0, 0.0, 0.0, 0.0, 0.0
            
            # Calculate failure rate
            failure_rate = (failed_pings / total_pings) * 100
            
            # Calculate average ping time (excluding None values for failed pings)
            successful_pings = [t for t in all_ping_times if t is not None]
            
            if successful_pings:
                avg_ping_time = sum(successful_pings) / len(successful_pings)
                min_ping_time = min(successful_pings)
                max_ping_time = max(successful_pings)
            else:
                avg_ping_time = min_ping_time = max_ping_time = 0.0
            
            # Calculate average failed pings over the last N non-overlapping windows
            # Each window is DEFAULT_MAX_POINTS long
            window_size = DEFAULT_MAX_POINTS
            num_windows = DEFAULT_NUM_WINDOWS
            total_ping_count = len(all_ping_times)
            
            if total_ping_count >= num_windows * window_size:
                # We have enough data for N full windows
                window_failed_counts = []
                
                for window_idx in range(num_windows):
                    window_start = total_ping_count - (num_windows - window_idx) * window_size
                    window_end = total_ping_count - (num_windows - window_idx - 1) * window_size
                    
                    # Count failed pings in this window (None values represent failed pings)
                    window_failed = sum(1 for i in range(window_start, window_end) 
                                     if i < len(all_ping_times) and all_ping_times[i] is None)
                    window_failed_counts.append(window_failed)
                
                avg_failed_pings = sum(window_failed_counts) / float(num_windows)
            else:
                # Not enough data for N full windows, use available data
                failed_in_available = sum(1 for ping_time in all_ping_times if ping_time is None)
                avg_failed_pings = float(failed_in_available)
            
            return failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return 0.0, 0.0, 0.0, 0.0, 0.0