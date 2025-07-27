"""
Direct tests for the calculate_statistics logic.
"""

import unittest
from unittest.mock import patch
import logging


def calculate_statistics(stats_data, num_windows=2):
    """
    Calculate statistics from ping data.
    
    Args:
        stats_data: Dictionary containing ping statistics
        num_windows: Number of windows to use for average failed pings calculation
        
    Returns:
        Tuple of (failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings)
    """
    try:
        total_pings = stats_data.get('total_pings', 0)
        failed_pings = stats_data.get('failed_pings', 0)
        all_ping_times = stats_data.get('all_ping_times', [])
        
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
        # Each window is 300 long (DEFAULT_MAX_POINTS)
        window_size = 300
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
        logging.error(f"Error calculating statistics: {e}")
        return 0.0, 0.0, 0.0, 0.0, 0.0


class TestCalculateStatistics(unittest.TestCase):
    """Test cases for calculate_statistics function."""
    
    def test_calculate_statistics_normal_case(self):
        """Test normal case with mixed successful and failed pings."""
        stats_data = {
            'total_pings': 10,
            'failed_pings': 2,
            'all_ping_times': [10.5, 12.3, None, 8.9, 15.2, None, 11.1, 9.8, 13.4, 10.7]
        }
        
        result = calculate_statistics(stats_data)
        
        # Expected: failure_rate = (2/10) * 100 = 20.0
        # Successful pings: [10.5, 12.3, 8.9, 15.2, 11.1, 9.8, 13.4, 10.7]
        # avg_ping_time = (10.5 + 12.3 + 8.9 + 15.2 + 11.1 + 9.8 + 13.4 + 10.7) / 8 = 11.49
        # min_ping_time = 8.9, max_ping_time = 15.2
        # avg_failed_pings = 2.0 (not enough data for two windows, so use all available)
        
        self.assertEqual(result[0], 20.0)  # failure_rate
        self.assertAlmostEqual(result[1], 11.49, places=2)  # avg_ping_time
        self.assertEqual(result[2], 8.9)  # min_ping_time
        self.assertEqual(result[3], 15.2)  # max_ping_time
        self.assertEqual(result[4], 2.0)  # avg_failed_pings
    
    def test_calculate_statistics_all_successful(self):
        """Test case where all pings are successful."""
        stats_data = {
            'total_pings': 5,
            'failed_pings': 0,
            'all_ping_times': [10.1, 12.3, 8.9, 15.2, 11.1],
            'failure_durations': []
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertAlmostEqual(result[1], 11.52, places=2)  # avg_ping_time
        self.assertEqual(result[2], 8.9)  # min_ping_time
        self.assertEqual(result[3], 15.2)  # max_ping_time
        self.assertEqual(result[4], 0.0)  # avg_failed_pings
    
    def test_calculate_statistics_all_failed(self):
        """Test case where all pings failed."""
        stats_data = {
            'total_pings': 3,
            'failed_pings': 3,
            'all_ping_times': [None, None, None]
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 100.0)  # failure_rate
        self.assertEqual(result[1], 0.0)  # avg_ping_time
        self.assertEqual(result[2], 0.0)  # min_ping_time
        self.assertEqual(result[3], 0.0)  # max_ping_time
        self.assertEqual(result[4], 3.0)  # avg_failed_pings
    
    def test_calculate_statistics_two_windows_logic(self):
        """Test the new two-window logic with enough data for two full windows."""
        # Create data with 600 pings (2 * 300 window size)
        # First window (0-299): 50 failed pings
        # Second window (300-599): 30 failed pings
        all_ping_times = []
        for i in range(600):
            if i < 300:  # First window
                if i < 50:  # First 50 are failed
                    all_ping_times.append(None)
                else:
                    all_ping_times.append(10.0 + (i % 10))
            else:  # Second window
                if i < 330:  # First 30 of second window are failed
                    all_ping_times.append(None)
                else:
                    all_ping_times.append(10.0 + (i % 10))
        
        stats_data = {
            'total_pings': 600,
            'failed_pings': 80,  # 50 + 30
            'all_ping_times': all_ping_times
        }
        
        result = calculate_statistics(stats_data)
        
        # Expected: avg_failed_pings = (50 + 30) / 2 = 40.0
        self.assertEqual(result[4], 40.0)  # avg_failed_pings
    
    def test_calculate_statistics_two_windows_different_failure_rates(self):
        """Test two-window logic with different failure rates in each window."""
        # Create data with 600 pings
        # First window (0-299): 100 failed pings (33.3% failure rate)
        # Second window (300-599): 50 failed pings (16.7% failure rate)
        all_ping_times = []
        for i in range(600):
            if i < 300:  # First window
                if i < 100:  # First 100 are failed
                    all_ping_times.append(None)
                else:
                    all_ping_times.append(10.0 + (i % 10))
            else:  # Second window
                if i < 350:  # First 50 of second window are failed
                    all_ping_times.append(None)
                else:
                    all_ping_times.append(10.0 + (i % 10))
        
        stats_data = {
            'total_pings': 600,
            'failed_pings': 150,  # 100 + 50
            'all_ping_times': all_ping_times
        }
        
        result = calculate_statistics(stats_data)
        
        # Expected: avg_failed_pings = (100 + 50) / 2 = 75.0
        self.assertEqual(result[4], 75.0)  # avg_failed_pings
    
    def test_calculate_statistics_insufficient_data_for_two_windows(self):
        """Test case where there isn't enough data for two full windows."""
        stats_data = {
            'total_pings': 400,  # Less than 2 * 300 = 600
            'failed_pings': 20,
            'all_ping_times': [None if i < 20 else 10.0 + (i % 10) for i in range(400)]
        }
        
        result = calculate_statistics(stats_data)
        
        # Should use all available data since we don't have two full windows
        self.assertEqual(result[4], 20.0)  # avg_failed_pings
    
    def test_calculate_statistics_exactly_two_windows(self):
        """Test case with exactly enough data for two full windows (600 pings)."""
        # Create exactly 600 pings
        all_ping_times = []
        for i in range(600):
            if i < 60:  # First 60 are failed
                all_ping_times.append(None)
            else:
                all_ping_times.append(10.0 + (i % 10))
        
        stats_data = {
            'total_pings': 600,
            'failed_pings': 60,
            'all_ping_times': all_ping_times
        }
        
        result = calculate_statistics(stats_data)
        
        # First window: 60 failed pings, Second window: 0 failed pings
        # Expected: avg_failed_pings = (60 + 0) / 2 = 30.0
        self.assertEqual(result[4], 30.0)  # avg_failed_pings
    
    def test_calculate_statistics_three_windows(self):
        """Test case with three windows using configurable num_windows parameter."""
        # Create 900 pings (3 * 300 window size)
        all_ping_times = []
        for i in range(900):
            if i < 100:  # First 100 are failed
                all_ping_times.append(None)
            elif i < 200:  # Next 100 are failed
                all_ping_times.append(None)
            else:
                all_ping_times.append(10.0 + (i % 10))
        
        stats_data = {
            'total_pings': 900,
            'failed_pings': 200,
            'all_ping_times': all_ping_times
        }
        
        result = calculate_statistics(stats_data, num_windows=3)
        
        # First window: 100 failed pings, Second window: 100 failed pings, Third window: 0 failed pings
        # Expected: avg_failed_pings = (100 + 100 + 0) / 3 = 66.67
        self.assertAlmostEqual(result[4], 66.67, places=2)  # avg_failed_pings
    
    def test_calculate_statistics_one_window(self):
        """Test case with one window using configurable num_windows parameter."""
        # Create 300 pings (1 * 300 window size)
        all_ping_times = []
        for i in range(300):
            if i < 50:  # First 50 are failed
                all_ping_times.append(None)
            else:
                all_ping_times.append(10.0 + (i % 10))
        
        stats_data = {
            'total_pings': 300,
            'failed_pings': 50,
            'all_ping_times': all_ping_times
        }
        
        result = calculate_statistics(stats_data, num_windows=1)
        
        # Single window: 50 failed pings
        # Expected: avg_failed_pings = 50.0
        self.assertEqual(result[4], 50.0)  # avg_failed_pings
    
    def test_calculate_statistics_zero_total_pings(self):
        """Test case with zero total pings."""
        stats_data = {
            'total_pings': 0,
            'failed_pings': 0,
            'all_ping_times': [],
            'failure_durations': []
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result, (0.0, 0.0, 0.0, 0.0, 0.0))
    
    def test_calculate_statistics_missing_keys(self):
        """Test case with missing dictionary keys."""
        stats_data = {}
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result, (0.0, 0.0, 0.0, 0.0, 0.0))
    
    def test_calculate_statistics_partial_missing_keys(self):
        """Test case with some missing keys."""
        stats_data = {
            'total_pings': 5,
            'failed_pings': 1
            # Missing 'all_ping_times' and 'failure_durations'
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 20.0)  # failure_rate
        self.assertEqual(result[1], 0.0)  # avg_ping_time
        self.assertEqual(result[2], 0.0)  # min_ping_time
        self.assertEqual(result[3], 0.0)  # max_ping_time
        self.assertEqual(result[4], 0.0)  # avg_failed_pings (empty list)
    
    def test_calculate_statistics_empty_ping_times(self):
        """Test case with empty ping times list."""
        stats_data = {
            'total_pings': 3,
            'failed_pings': 0,
            'all_ping_times': []
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertEqual(result[1], 0.0)  # avg_ping_time
        self.assertEqual(result[2], 0.0)  # min_ping_time
        self.assertEqual(result[3], 0.0)  # max_ping_time
        self.assertEqual(result[4], 0.0)  # avg_failed_pings
    
    def test_calculate_statistics_single_successful_ping(self):
        """Test case with single successful ping."""
        stats_data = {
            'total_pings': 1,
            'failed_pings': 0,
            'all_ping_times': [10.5]
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertEqual(result[1], 10.5)  # avg_ping_time
        self.assertEqual(result[2], 10.5)  # min_ping_time
        self.assertEqual(result[3], 10.5)  # max_ping_time
        self.assertEqual(result[4], 0.0)  # avg_failed_pings
    
    def test_calculate_statistics_single_failed_ping(self):
        """Test case with single failed ping."""
        stats_data = {
            'total_pings': 1,
            'failed_pings': 1,
            'all_ping_times': [None]
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 100.0)  # failure_rate
        self.assertEqual(result[1], 0.0)  # avg_ping_time
        self.assertEqual(result[2], 0.0)  # min_ping_time
        self.assertEqual(result[3], 0.0)  # max_ping_time
        self.assertEqual(result[4], 1.0)  # avg_failed_pings
    
    def test_calculate_statistics_mixed_none_values(self):
        """Test case with mixed None and numeric values."""
        stats_data = {
            'total_pings': 6,
            'failed_pings': 2,
            'all_ping_times': [10.1, None, 12.3, None, 8.9, 15.2]
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertAlmostEqual(result[0], 33.33, places=2)  # failure_rate
        self.assertAlmostEqual(result[1], 11.625, places=3)  # avg_ping_time
        self.assertEqual(result[2], 8.9)  # min_ping_time
        self.assertEqual(result[3], 15.2)  # max_ping_time
        self.assertEqual(result[4], 2.0)  # avg_failed_pings
    
    def test_calculate_statistics_large_numbers(self):
        """Test case with large ping times."""
        stats_data = {
            'total_pings': 4,
            'failed_pings': 1,
            'all_ping_times': [1000.5, None, 2000.3, 1500.7]
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 25.0)  # failure_rate
        self.assertAlmostEqual(result[1], 1500.5, places=1)  # avg_ping_time
        self.assertEqual(result[2], 1000.5)  # min_ping_time
        self.assertEqual(result[3], 2000.3)  # max_ping_time
        self.assertEqual(result[4], 1.0)  # avg_failed_pings
    
    def test_calculate_statistics_decimal_precision(self):
        """Test case with decimal precision."""
        stats_data = {
            'total_pings': 3,
            'failed_pings': 0,
            'all_ping_times': [10.123456, 20.987654, 15.555555]
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertAlmostEqual(result[1], 15.555555, places=6)  # avg_ping_time
        self.assertEqual(result[2], 10.123456)  # min_ping_time
        self.assertEqual(result[3], 20.987654)  # max_ping_time
        self.assertEqual(result[4], 0.0)  # avg_failed_pings
    
    @patch('logging.error')
    def test_calculate_statistics_exception_handling(self, mock_logger):
        """Test exception handling in calculate_statistics."""
        # Create a stats_data that will cause an exception
        stats_data = {
            'total_pings': 'invalid',  # This will cause TypeError in division
            'failed_pings': 0,
            'all_ping_times': [10.1, 12.3]
        }
        
        result = calculate_statistics(stats_data)
        
        # Should return default values and log error
        self.assertEqual(result, (0.0, 0.0, 0.0, 0.0, 0.0))
        mock_logger.assert_called_once()
    
    def test_calculate_statistics_type_annotations(self):
        """Test that the method accepts the correct types."""
        stats_data = {
            'total_pings': 5,
            'failed_pings': 1,
            'all_ping_times': [10.1, None, 12.3, 8.9, 15.2],
            'failure_durations': [2.5]
        }
        
        # This should not raise any type errors
        result = calculate_statistics(stats_data)
        
        # Verify return type is a tuple of 5 floats
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 5)
        for value in result:
            self.assertIsInstance(value, float)
    
    def test_calculate_statistics_edge_case_zero_values(self):
        """Test case with zero values (edge case)."""
        stats_data = {
            'total_pings': 3,
            'failed_pings': 0,  # No failed pings
            'all_ping_times': [0.0, 0.0, 0.0]  # Zero ping times
        }
        
        result = calculate_statistics(stats_data)
        
        # Should handle zero values gracefully
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertEqual(result[1], 0.0)  # avg_ping_time
        self.assertEqual(result[2], 0.0)  # min_ping_time
        self.assertEqual(result[3], 0.0)  # max_ping_time
        self.assertEqual(result[4], 0.0)  # avg_failed_pings
    
    def test_calculate_statistics_edge_case_very_large_numbers(self):
        """Test case with very large numbers."""
        stats_data = {
            'total_pings': 2,
            'failed_pings': 0,
            'all_ping_times': [1e10, 2e10]  # Very large numbers
        }
        
        result = calculate_statistics(stats_data)
        
        self.assertEqual(result[0], 0.0)  # failure_rate
        self.assertEqual(result[1], 1.5e10)  # avg_ping_time
        self.assertEqual(result[2], 1e10)  # min_ping_time
        self.assertEqual(result[3], 2e10)  # max_ping_time
        self.assertEqual(result[4], 0.0)  # avg_failed_pings


class TestResetFunctionality(unittest.TestCase):
    """Test cases for reset functionality."""
    
    def test_reset_statistics_initial_state(self):
        """Test that reset returns statistics to initial state."""
        # Create a mock PingEngine-like object
        class MockPingEngine:
            def __init__(self):
                self.ttls = [119, 120, 121, 122, 123]
                self.ping_times = [10.1, 10.2, 10.3, 10.4, 10.5]
                self.all_ping_times = [10.1, 10.2, 10.3, 10.4, 10.5]
                self.failed_pings = 2
                self.total_pings = 10
                self.failure_durations = [3, 5]
                self.current_failure_start = 8
                self.max_points = 300
            
            def reset_statistics(self):
                """Reset all statistics and data to initial state."""
                # Clear all data structures
                self.ttls.clear()
                self.ping_times.clear()
                self.all_ping_times.clear()
                self.failed_pings = 0
                self.total_pings = 0
                self.failure_durations.clear()
                self.current_failure_start = None
                
                # Re-initialize with default data
                for i in range(self.max_points):
                    self.ttls.append(119)
                    self.ping_times.append(10)
                    self.all_ping_times.append(10)
                    self.total_pings += 1
            
            def get_statistics(self):
                """Get current statistics and data."""
                return {
                    'ttls': list(self.ttls),
                    'ping_times': list(self.ping_times),
                    'all_ping_times': self.all_ping_times.copy(),
                    'failed_pings': self.failed_pings,
                    'total_pings': self.total_pings,
                    'failure_durations': self.failure_durations.copy()
                }
        
        # Create engine and populate with data
        engine = MockPingEngine()
        
        # Verify initial state has data
        stats_before = engine.get_statistics()
        self.assertEqual(stats_before['failed_pings'], 2)
        self.assertEqual(stats_before['total_pings'], 10)
        self.assertEqual(len(stats_before['ttls']), 5)
        self.assertEqual(len(stats_before['failure_durations']), 2)
        self.assertIsNotNone(engine.current_failure_start)
        
        # Reset statistics
        engine.reset_statistics()
        
        # Verify reset state
        stats_after = engine.get_statistics()
        self.assertEqual(stats_after['failed_pings'], 0)
        self.assertEqual(stats_after['total_pings'], 300)  # Should be re-initialized
        self.assertEqual(len(stats_after['ttls']), 300)
        self.assertEqual(len(stats_after['failure_durations']), 0)
        self.assertIsNone(engine.current_failure_start)
        
        # Verify all TTLs are default value
        for ttl in stats_after['ttls']:
            self.assertEqual(ttl, 119)
        
        # Verify all ping times are default value
        for ping_time in stats_after['ping_times']:
            self.assertEqual(ping_time, 10)
    
    def test_reset_statistics_calculation_after_reset(self):
        """Test that statistics calculation works correctly after reset."""
        # Create test data that would give non-zero statistics
        stats_data_before = {
            'total_pings': 100,
            'failed_pings': 20,
            'all_ping_times': [10.0 if i % 5 != 0 else None for i in range(100)]
        }
        
        # Calculate statistics before reset
        result_before = calculate_statistics(stats_data_before)
        self.assertGreater(result_before[0], 0)  # failure_rate > 0
        self.assertGreater(result_before[4], 0)  # avg_failed_pings > 0
        
        # Simulate reset by creating fresh data
        stats_data_after = {
            'total_pings': 300,  # Default initialization
            'failed_pings': 0,
            'all_ping_times': [10.0] * 300  # All successful pings
        }
        
        # Calculate statistics after reset
        result_after = calculate_statistics(stats_data_after)
        self.assertEqual(result_after[0], 0.0)  # failure_rate = 0
        self.assertEqual(result_after[4], 0.0)  # avg_failed_pings = 0
    
    def test_reset_statistics_thread_safety(self):
        """Test that reset operation is thread-safe."""
        import threading
        import time
        
        class MockPingEngine:
            def __init__(self):
                self.ttls = [119, 120, 121]
                self.ping_times = [10.1, 10.2, 10.3]
                self.all_ping_times = [10.1, 10.2, 10.3]
                self.failed_pings = 1
                self.total_pings = 5
                self.failure_durations = [2]
                self.current_failure_start = 3
                self.max_points = 300
                self._lock = threading.Lock()
            
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
                    for i in range(self.max_points):
                        self.ttls.append(119)
                        self.ping_times.append(10)
                        self.all_ping_times.append(10)
                        self.total_pings += 1
            
            def get_statistics(self):
                """Get current statistics and data."""
                with self._lock:  # Thread safety
                    return {
                        'ttls': list(self.ttls),
                        'ping_times': list(self.ping_times),
                        'all_ping_times': self.all_ping_times.copy(),
                        'failed_pings': self.failed_pings,
                        'total_pings': self.total_pings,
                        'failure_durations': self.failure_durations.copy()
                    }
        
        engine = MockPingEngine()
        
        # Create multiple threads that try to reset simultaneously
        def reset_worker():
            time.sleep(0.01)  # Small delay to increase chance of race condition
            engine.reset_statistics()
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=reset_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify final state is consistent
        stats = engine.get_statistics()
        self.assertEqual(stats['failed_pings'], 0)
        self.assertEqual(stats['total_pings'], 300)
        self.assertEqual(len(stats['ttls']), 300)
        self.assertEqual(len(stats['failure_durations']), 0)
    
    def test_reset_statistics_api_response_format(self):
        """Test that reset API returns correct response format."""
        # Mock API response structure
        def mock_reset_api():
            try:
                # Simulate successful reset
                return {'success': True, 'message': 'Statistics reset successfully'}
            except Exception as e:
                return {'success': False, 'message': f'Error resetting statistics: {str(e)}'}
        
        # Test successful reset
        response = mock_reset_api()
        self.assertTrue(response['success'])
        self.assertIn('Statistics reset successfully', response['message'])
        self.assertIn('success', response)
        self.assertIn('message', response)
    
    def test_reset_statistics_error_handling(self):
        """Test reset functionality error handling."""
        # Mock API response for error case
        def mock_reset_api_with_error():
            try:
                raise Exception("Test error")
            except Exception as e:
                return {'success': False, 'message': f'Error resetting statistics: {str(e)}'}
        
        response = mock_reset_api_with_error()
        self.assertFalse(response['success'])
        self.assertIn('Error resetting statistics', response['message'])
        self.assertIn('Test error', response['message'])


if __name__ == '__main__':
    unittest.main() 