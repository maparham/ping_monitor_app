"""Statistics calculation for ping monitoring."""

from typing import Dict, Tuple, List, Optional
from .config import DEFAULT_NUM_WINDOWS

class StatisticsCalculator:
    """Calculates network statistics from ping data."""
    
    @staticmethod
    def calculate_statistics(stats_data: Dict, num_windows: int = DEFAULT_NUM_WINDOWS) -> Tuple[float, Optional[float], Optional[float], Optional[float], float]:
        """Calculate statistics from ping data."""
        try:
            total_pings = stats_data.get('total_pings', 0)
            failed_pings = stats_data.get('failed_pings', 0)
            ping_times: List[Optional[float]] = stats_data.get('ping_times', [])
            
            # Get window-based failed pings data
            failed_pings_per_window: List[int] = stats_data.get('failed_pings_per_window', [])
            current_window_failed: int = stats_data.get('current_window_failed', 0)
            current_window_total: int = stats_data.get('current_window_total', 0)
            
            if total_pings == 0:
                return 0.0, None, None, None, 0.0
            
            # Calculate failure rate
            failure_rate = (failed_pings / total_pings) * 100
            
            # Calculate ping time statistics (excluding None values)
            successful_pings = [t for t in ping_times if t is not None]
            
            if successful_pings:
                avg_ping_time = sum(successful_pings) / len(successful_pings)
                min_ping_time = min(successful_pings)
                max_ping_time = max(successful_pings)
            else:
                avg_ping_time = min_ping_time = max_ping_time = None
            
            # Calculate avg_failed_pings using sliding window logic
            # Get the last N completed windows plus current window if it has data
            window_failed_counts = list(failed_pings_per_window)
            
            # If current window has data, include it in the calculation
            if current_window_total > 0:
                window_failed_counts.append(current_window_failed)
            
            # Calculate average over available windows (up to num_windows)
            if len(window_failed_counts) > 0:
                # Take the last N windows if we have more than N
                recent_windows = window_failed_counts[-num_windows:] if len(window_failed_counts) >= num_windows else window_failed_counts
                avg_failed_pings = sum(recent_windows) / len(recent_windows)
            else:
                avg_failed_pings = 0.0
            
            return failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings
            
        except Exception:
            return 0.0, None, None, None, 0.0