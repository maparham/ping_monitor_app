"""Statistics calculation for ping monitoring."""

from typing import Dict, Tuple, List, Optional

class StatisticsCalculator:
    """Calculates network statistics from ping data."""
    
    @staticmethod
    def calculate_statistics(stats_data: Dict) -> Tuple[float, Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Calculate statistics from ping data."""
        try:
            # Get pre-calculated failure rate from ping engine
            failure_rate = stats_data.get('failure_rate', 0.0)
            ping_times: List[Optional[float]] = stats_data.get('ping_times', [])
            
            # Get outage history data
            outage_history: List[int] = stats_data.get('outage_history', [])
            
            if not ping_times:
                return failure_rate, None, None, None, None
            
            # Calculate ping time statistics (excluding None values)
            successful_pings = [t for t in ping_times if t is not None]
            
            if successful_pings:
                avg_ping_time = sum(successful_pings) / len(successful_pings)
                min_ping_time = min(successful_pings)
                max_ping_time = max(successful_pings)
            else:
                avg_ping_time = min_ping_time = max_ping_time = None
            
            # Calculate average outage duration
            if outage_history:
                avg_outage_duration = sum(outage_history) / len(outage_history)
            else:
                avg_outage_duration = None
            
            return failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_outage_duration
            
        except Exception:
            return 0.0, None, None, None, None