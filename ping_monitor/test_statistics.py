"""Tests for statistics calculation functionality."""

import unittest
from statistics import StatisticsCalculator

class TestStatisticsCalculator(unittest.TestCase):
    """Test cases for StatisticsCalculator class."""

    def test_calculate_statistics_empty_data(self):
        """Test statistics calculation with empty data."""
        stats_data = {}
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertIsNone(result[1])  # avg_ping_time
        self.assertIsNone(result[2])  # min_ping_time
        self.assertIsNone(result[3])  # max_ping_time
        self.assertIsNone(result[4])  # avg_outage_duration

    def test_calculate_statistics_single_ping(self):
        """Test statistics calculation with single ping."""
        stats_data = {
            'failure_rate': 0.0,
            'ping_times': [15.2],
            'outage_history': []
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertEqual(result[1], 15.2)  # avg_ping_time
        self.assertEqual(result[2], 15.2)  # min_ping_time
        self.assertEqual(result[3], 15.2)  # max_ping_time
        self.assertIsNone(result[4])  # avg_outage_duration

    def test_calculate_statistics_all_successful(self):
        """Test statistics calculation with all successful pings."""
        stats_data = {
            'failure_rate': 0.0,
            'ping_times': [10.5, 12.3, 11.8, 13.1, 10.9],
            'outage_history': []
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertEqual(result[1], 11.72)  # avg_ping_time
        self.assertEqual(result[2], 10.5)  # min_ping_time
        self.assertEqual(result[3], 13.1)  # max_ping_time
        self.assertIsNone(result[4])  # avg_outage_duration

    def test_calculate_statistics_all_failed(self):
        """Test statistics calculation with all failed pings."""
        stats_data = {
            'failure_rate': 100.0,
            'ping_times': [None, None, None, None, None],
            'outage_history': [5]  # One outage of duration 5
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 100.0)  # failure_rate
        self.assertIsNone(result[1])  # avg_ping_time
        self.assertIsNone(result[2])  # min_ping_time
        self.assertIsNone(result[3])  # max_ping_time
        self.assertEqual(result[4], 5.0)  # avg_outage_duration

    def test_calculate_statistics_mixed_success_failure(self):
        """Test statistics calculation with mixed success and failure."""
        stats_data = {
            'failure_rate': 30.0,
            'ping_times': [10.5, None, None, 12.3, 11.8, 13.1, 10.9, 12.0, 11.5, 10.8],
            'outage_history': [2]  # One outage of duration 2
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 30.0)  # failure_rate
        self.assertAlmostEqual(result[1], 11.61, places=2)  # avg_ping_time (only successful ones)
        self.assertEqual(result[2], 10.5)  # min_ping_time
        self.assertEqual(result[3], 13.1)  # max_ping_time
        self.assertEqual(result[4], 2.0)  # avg_outage_duration

    def test_calculate_statistics_with_current_window(self):
        """Test statistics calculation including current window data."""
        stats_data = {
            'failure_rate': 50.0,
            'ping_times': [None, 15.2],
            'outage_history': [1]  # One outage of duration 1
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 50.0)  # failure_rate
        self.assertEqual(result[1], 15.2)  # avg_ping_time
        self.assertEqual(result[2], 15.2)  # min_ping_time
        self.assertEqual(result[3], 15.2)  # max_ping_time
        self.assertEqual(result[4], 1.0)  # avg_outage_duration

    def test_calculate_statistics_current_window_zero_total(self):
        """Test statistics calculation when current window has zero total."""
        stats_data = {
            'total_pings': 0,
            'failed_pings': 0,
            'ping_times': [],
            'outage_history': []
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertIsNone(result[1])  # avg_ping_time
        self.assertIsNone(result[2])  # min_ping_time
        self.assertIsNone(result[3])  # max_ping_time
        self.assertIsNone(result[4])  # avg_outage_duration

    def test_calculate_statistics_edge_case_single_failed_ping(self):
        """Test statistics calculation with single failed ping."""
        stats_data = {
            'failure_rate': 100.0,
            'ping_times': [None],
            'outage_history': []
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 100.0)  # failure_rate
        self.assertIsNone(result[1])  # avg_ping_time
        self.assertIsNone(result[2])  # min_ping_time
        self.assertIsNone(result[3])  # max_ping_time
        self.assertIsNone(result[4])  # avg_outage_duration

    def test_calculate_statistics_edge_case_single_ping(self):
        """Test statistics calculation with single ping."""
        stats_data = {
            'failure_rate': 0.0,
            'ping_times': [15.2],
            'outage_history': []
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertEqual(result[1], 15.2)  # avg_ping_time
        self.assertEqual(result[2], 15.2)  # min_ping_time
        self.assertEqual(result[3], 15.2)  # max_ping_time
        self.assertIsNone(result[4])  # avg_outage_duration

    def test_calculate_statistics_exception_handling(self):
        """Test statistics calculation with exception handling."""
        # Test with invalid data that would cause division by zero
        stats_data = {
            'failure_rate': 0.0,
            'ping_times': [],
            'outage_history': []
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        # Should return safe defaults
        self.assertEqual(result[0], 0.0)
        self.assertIsNone(result[1])
        self.assertIsNone(result[2])
        self.assertIsNone(result[3])
        self.assertIsNone(result[4])

    def test_calculate_statistics_missing_keys(self):
        """Test statistics calculation with missing dictionary keys."""
        stats_data = {}  # Empty dictionary
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        # Should return safe defaults
        self.assertEqual(result[0], 0.0)
        self.assertIsNone(result[1])
        self.assertIsNone(result[2])
        self.assertIsNone(result[3])
        self.assertIsNone(result[4])

    def test_calculate_statistics_partial_keys(self):
        """Test statistics calculation with partial dictionary keys."""
        stats_data = {
            'failure_rate': 40.0
            # Missing ping_times and outage_history
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 40.0)  # failure_rate
        self.assertIsNone(result[1])  # avg_ping_time
        self.assertIsNone(result[2])  # min_ping_time
        self.assertIsNone(result[3])  # max_ping_time
        self.assertIsNone(result[4])  # avg_outage_duration

    def test_calculate_statistics_missing_failure_rate(self):
        """Test statistics calculation when failure_rate is missing."""
        stats_data = {
            # Missing failure_rate, ping_times and outage_history
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate default
        self.assertIsNone(result[1])  # avg_ping_time
        self.assertIsNone(result[2])  # min_ping_time
        self.assertIsNone(result[3])  # max_ping_time
        self.assertIsNone(result[4])  # avg_outage_duration

    def test_calculate_statistics_multiple_outages(self):
        """Test statistics calculation with multiple outages."""
        stats_data = {
            'failure_rate': 53.33,
            'ping_times': [10.5, None, None, 12.3, None, None, None, 13.1, 10.9, 12.0, 11.5, 10.8, 12.2, 11.9, 10.7],
            'outage_history': [2, 3, 3]  # Three outages with durations 2, 3, 3
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        self.assertAlmostEqual(result[0], 53.33, places=2)  # failure_rate
        self.assertAlmostEqual(result[1], 11.59, places=2)  # avg_ping_time (only successful ones)
        self.assertEqual(result[2], 10.5)  # min_ping_time
        self.assertEqual(result[3], 13.1)  # max_ping_time
        self.assertAlmostEqual(result[4], 2.67, places=2)  # avg_outage_duration (2+3+3)/3 = 2.67

    def test_calculate_statistics_sliding_window_failure_rate(self):
        """Test that statistics calculator uses pre-calculated sliding window failure rate."""
        # Test with data that would have different global vs window failure rates
        stats_data = {
            'failure_rate': 25.0,  # Pre-calculated from sliding window
            'ping_times': [10.5, None, 12.3, 11.8],  # 1 failed out of 4 in window = 25%
            'outage_history': []
        }
        result = StatisticsCalculator.calculate_statistics(stats_data)
        
        # Should use the pre-calculated failure rate, not calculate from ping_times
        self.assertEqual(result[0], 25.0)  # failure_rate from sliding window
        self.assertAlmostEqual(result[1], 11.53, places=2)  # avg_ping_time (only successful ones)


if __name__ == '__main__':
    unittest.main() 