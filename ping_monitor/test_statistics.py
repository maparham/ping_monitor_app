"""Unit tests for statistics module."""

import unittest
from ping_monitor.statistics import StatisticsCalculator
from ping_monitor.config import DEFAULT_NUM_WINDOWS


class TestStatisticsCalculator(unittest.TestCase):
    """Test cases for StatisticsCalculator class."""
    
    def test_calculate_statistics_empty_data(self):
        """Test statistics calculation with empty data."""
        stats_data = {
            'total_pings': 0,
            'failed_pings': 0,
            'ping_times': [],
            'failed_pings_per_window': [],
            'current_window_failed': 0,
            'current_window_total': 0
        }
        
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result, (0.0, None, None, None, 0.0))
    
    def test_calculate_statistics_all_successful(self):
        """Test statistics calculation with all successful pings."""
        stats_data = {
            'total_pings': 5,
            'failed_pings': 0,
            'ping_times': [10.5, 12.3, 11.8, 13.1, 10.9],
            'failed_pings_per_window': [],
            'current_window_failed': 0,
            'current_window_total': 5
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(failure_rate, 0.0)
        self.assertAlmostEqual(avg_ping_time, 11.72, places=2)
        self.assertEqual(min_ping_time, 10.5)
        self.assertEqual(max_ping_time, 13.1)
        self.assertEqual(avg_failed_pings, 0.0)
    
    def test_calculate_statistics_all_failed(self):
        """Test statistics calculation with all failed pings."""
        stats_data = {
            'total_pings': 5,
            'failed_pings': 5,
            'ping_times': [None, None, None, None, None],
            'failed_pings_per_window': [],
            'current_window_failed': 5,
            'current_window_total': 5
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(failure_rate, 100.0)
        self.assertIsNone(avg_ping_time)
        self.assertIsNone(min_ping_time)
        self.assertIsNone(max_ping_time)
        self.assertEqual(avg_failed_pings, 5.0)
    
    def test_calculate_statistics_mixed_success_failure(self):
        """Test statistics calculation with mixed success and failure."""
        stats_data = {
            'total_pings': 10,
            'failed_pings': 3,
            'ping_times': [10.5, None, 12.3, 11.8, None, 13.1, 10.9, None, 12.0, 11.5],
            'failed_pings_per_window': [2],
            'current_window_failed': 1,
            'current_window_total': 10
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(failure_rate, 30.0)
        self.assertAlmostEqual(avg_ping_time, 11.73, places=2)
        self.assertEqual(min_ping_time, 10.5)
        self.assertEqual(max_ping_time, 13.1)
        self.assertAlmostEqual(avg_failed_pings, 1.5, places=1)  # (2+1)/2 = 1.5
    
    def test_calculate_statistics_with_multiple_windows(self):
        """Test statistics calculation with multiple windows."""
        stats_data = {
            'total_pings': 15,
            'failed_pings': 6,
            'ping_times': [10.5, 12.3, 11.8, 13.1, 10.9] * 3,  # 15 successful pings
            'failed_pings_per_window': [2, 3, 1],
            'current_window_failed': 0,
            'current_window_total': 0
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data, num_windows=2)
        
        self.assertEqual(failure_rate, 40.0)  # 6/15 * 100
        self.assertAlmostEqual(avg_ping_time, 11.72, places=2)
        self.assertEqual(min_ping_time, 10.5)
        self.assertEqual(max_ping_time, 13.1)
        self.assertEqual(avg_failed_pings, 2.0)  # Average of last 2 windows: (3+1)/2 = 2
    
    def test_calculate_statistics_with_custom_num_windows(self):
        """Test statistics calculation with custom number of windows."""
        stats_data = {
            'total_pings': 20,
            'failed_pings': 8,
            'ping_times': [10.5, 12.3, 11.8, 13.1, 10.9] * 4,  # 20 successful pings
            'failed_pings_per_window': [2, 3, 1, 2],
            'current_window_failed': 0,
            'current_window_total': 0
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data, num_windows=3)
        
        self.assertEqual(failure_rate, 40.0)  # 8/20 * 100
        self.assertAlmostEqual(avg_ping_time, 11.72, places=2)
        self.assertEqual(min_ping_time, 10.5)
        self.assertEqual(max_ping_time, 13.1)
        self.assertAlmostEqual(avg_failed_pings, 2.0, places=1)  # Average of last 3 windows: (1+2+3)/3 = 2
    
    def test_calculate_statistics_with_current_window(self):
        """Test statistics calculation including current window data."""
        stats_data = {
            'total_pings': 12,
            'failed_pings': 4,
            'ping_times': [10.5, 12.3, 11.8, 13.1, 10.9, 12.0, 11.5, 10.8, 12.2, 11.9, 10.7, 12.1],
            'failed_pings_per_window': [2, 1],
            'current_window_failed': 1,
            'current_window_total': 2
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data, num_windows=2)
        
        self.assertAlmostEqual(failure_rate, 33.33, places=2)  # 4/12 * 100
        self.assertAlmostEqual(avg_ping_time, 11.65, places=2)
        self.assertEqual(min_ping_time, 10.5)
        self.assertEqual(max_ping_time, 13.1)
        self.assertAlmostEqual(avg_failed_pings, 1.0, places=1)  # Average of last 2 windows: (1+1)/2 = 1.0
    
    def test_calculate_statistics_missing_keys(self):
        """Test statistics calculation with missing dictionary keys."""
        stats_data = {}
        
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result, (0.0, None, None, None, 0.0))
    
    def test_calculate_statistics_partial_keys(self):
        """Test statistics calculation with partial dictionary keys."""
        stats_data = {
            'total_pings': 5,
            'failed_pings': 2,
            'ping_times': [10.5, None, 12.3, None, 11.8]
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(failure_rate, 40.0)  # 2/5 * 100
        self.assertAlmostEqual(avg_ping_time, 11.53, places=2)  # (10.5+12.3+11.8)/3
        self.assertEqual(min_ping_time, 10.5)
        self.assertEqual(max_ping_time, 12.3)
        self.assertEqual(avg_failed_pings, 0.0)  # No window data
    
    def test_calculate_statistics_exception_handling(self):
        """Test statistics calculation with exception handling."""
        # Pass invalid data that would cause an exception
        stats_data = None
        
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result, (0.0, None, None, None, 0.0))
    
    def test_calculate_statistics_edge_case_single_ping(self):
        """Test statistics calculation with single ping."""
        stats_data = {
            'total_pings': 1,
            'failed_pings': 0,
            'ping_times': [15.2],
            'failed_pings_per_window': [],
            'current_window_failed': 0,
            'current_window_total': 1
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(failure_rate, 0.0)
        self.assertEqual(avg_ping_time, 15.2)
        self.assertEqual(min_ping_time, 15.2)
        self.assertEqual(max_ping_time, 15.2)
        self.assertEqual(avg_failed_pings, 0.0)
    
    def test_calculate_statistics_edge_case_single_failed_ping(self):
        """Test statistics calculation with single failed ping."""
        stats_data = {
            'total_pings': 1,
            'failed_pings': 1,
            'ping_times': [None],
            'failed_pings_per_window': [],
            'current_window_failed': 1,
            'current_window_total': 1
        }
        
        failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
            StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(failure_rate, 100.0)
        self.assertIsNone(avg_ping_time)
        self.assertIsNone(min_ping_time)
        self.assertIsNone(max_ping_time)
        self.assertEqual(avg_failed_pings, 1.0)


if __name__ == '__main__':
    unittest.main() 