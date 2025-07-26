"""
Statistics Module
Handles calculation of network statistics.
"""

import logging
from typing import Dict, Tuple, List, Optional
from .config import LOG_LEVEL, LOG_FORMAT

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
            Tuple of (failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failure_duration)
        """
        try:
            total_pings = stats_data.get('total_pings', 0)
            failed_pings = stats_data.get('failed_pings', 0)
            all_ping_times: List[Optional[float]] = stats_data.get('all_ping_times', [])
            failure_durations = stats_data.get('failure_durations', [])
            
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
            
            # Calculate average failure duration
            avg_failure_duration = sum(failure_durations) / len(failure_durations) if failure_durations else 0
            
            return failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failure_duration
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return 0.0, 0.0, 0.0, 0.0, 0.0
    
    @staticmethod
    def format_statistics(stats_data: Dict) -> Dict[str, str]:
        """
        Format statistics for display.
        
        Args:
            stats_data: Dictionary containing ping statistics
            
        Returns:
            Dictionary with formatted statistics strings
        """
        try:
            failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failure_duration = \
                StatisticsCalculator.calculate_statistics(stats_data)
            
            return {
                'failure_rate': f"{failure_rate:.1f}",
                'avg_ping_time': f"{avg_ping_time:.1f}",
                'min_ping_time': f"{min_ping_time:.1f}",
                'max_ping_time': f"{max_ping_time:.1f}",
                'avg_failure_duration': f"{avg_failure_duration:.1f}",
                'total_pings': str(stats_data.get('total_pings', 0))
            }
        except Exception as e:
            logger.error(f"Error formatting statistics: {e}")
            return {
                'failure_rate': "0.0",
                'avg_ping_time': "0.0",
                'min_ping_time': "0.0",
                'max_ping_time': "0.0",
                'avg_failure_duration': "0.0",
                'total_pings': "0"
            } 