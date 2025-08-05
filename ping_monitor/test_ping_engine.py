"""Tests for ping engine functionality."""

import unittest
from unittest.mock import patch, Mock
from ping_engine import PingEngine

class TestPingEngine(unittest.TestCase):
    """Test cases for PingEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.ping_engine = PingEngine(target="8.8.8.8", max_points=5)

    def tearDown(self):
        """Clean up after tests."""
        if self.ping_engine.is_running():
            self.ping_engine.stop()

    def test_initialization(self):
        """Test PingEngine initialization."""
        self.assertEqual(self.ping_engine.target, "8.8.8.8")
        self.assertEqual(self.ping_engine.max_points, 5)
        self.assertEqual(self.ping_engine.total_pings, 0)
        self.assertEqual(self.ping_engine.failed_pings, 0)
        self.assertEqual(len(self.ping_engine.ttls), 0)
        self.assertEqual(len(self.ping_engine.ping_times), 0)
        self.assertEqual(self.ping_engine.consecutive_failures, 0)
        self.assertEqual(self.ping_engine.outage_start_index, None)
        self.assertEqual(len(self.ping_engine.outage_history), 0)

    def test_initialization_with_custom_params(self):
        """Test PingEngine initialization with custom parameters."""
        engine = PingEngine(target="1.1.1.1", max_points=10)
        self.assertEqual(engine.target, "1.1.1.1")
        self.assertEqual(engine.max_points, 10)

    @patch('ping_engine.subprocess.run')
    def test_ping_target_success(self, mock_run):
        """Test successful ping operation."""
        # Mock successful ping response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "64 bytes from 8.8.8.8: icmp_seq=1 ttl=64 time=15.2 ms"
        mock_run.return_value = mock_result

        ttl, ping_time = self.ping_engine.ping_target()
        
        self.assertEqual(ttl, 64)
        self.assertEqual(ping_time, 15.2)
        mock_run.assert_called_once()

    @patch('ping_engine.subprocess.run')
    def test_ping_target_failure(self, mock_run):
        """Test failed ping operation."""
        # Mock failed ping response
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        ttl, ping_time = self.ping_engine.ping_target()
        
        self.assertIsNone(ttl)
        self.assertIsNone(ping_time)

    @patch('ping_engine.subprocess.run')
    def test_ping_target_timeout(self, mock_run):
        """Test ping operation with timeout."""
        mock_run.side_effect = TimeoutError()

        ttl, ping_time = self.ping_engine.ping_target()
        
        self.assertIsNone(ttl)
        self.assertIsNone(ping_time)

    @patch('ping_engine.subprocess.run')
    def test_ping_target_exception(self, mock_run):
        """Test ping operation with exception."""
        mock_run.side_effect = Exception("Network error")

        ttl, ping_time = self.ping_engine.ping_target()
        
        self.assertIsNone(ttl)
        self.assertIsNone(ping_time)

    def test_process_ping_result_success(self):
        """Test processing successful ping result."""
        initial_total = self.ping_engine.total_pings
        initial_failed = self.ping_engine.failed_pings
        
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        self.assertEqual(self.ping_engine.total_pings, initial_total + 1)
        self.assertEqual(self.ping_engine.failed_pings, initial_failed)
        self.assertEqual(len(self.ping_engine.ttls), 1)
        self.assertEqual(len(self.ping_engine.ping_times), 1)
        self.assertEqual(self.ping_engine.ttls[0], 64)
        self.assertEqual(self.ping_engine.ping_times[0], 15.2)
    
    def test_process_ping_result_failure(self):
        """Test processing failed ping result."""
        initial_total = self.ping_engine.total_pings
        initial_failed = self.ping_engine.failed_pings
        
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        self.assertEqual(self.ping_engine.total_pings, initial_total + 1)
        self.assertEqual(self.ping_engine.failed_pings, initial_failed + 1)
        self.assertEqual(len(self.ping_engine.ttls), 1)
        self.assertEqual(len(self.ping_engine.ping_times), 1)
        self.assertIsNone(self.ping_engine.ttls[0])
        self.assertIsNone(self.ping_engine.ping_times[0])
    
    def test_start_stop(self):
        """Test starting and stopping the ping engine."""
        self.assertFalse(self.ping_engine.is_running())
        
        self.ping_engine.start()
        self.assertTrue(self.ping_engine.is_running())
        
        self.ping_engine.stop()
        self.assertFalse(self.ping_engine.is_running())
    
    def test_reset(self):
        """Test resetting all statistics."""
        # Add some data first
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        self.assertEqual(self.ping_engine.total_pings, 2)
        self.assertEqual(self.ping_engine.failed_pings, 1)
        self.assertEqual(len(self.ping_engine.ttls), 2)
        self.assertEqual(len(self.ping_engine.ping_times), 2)
        
        self.ping_engine.reset()
        
        self.assertEqual(self.ping_engine.total_pings, 0)
        self.assertEqual(self.ping_engine.failed_pings, 0)
        self.assertEqual(len(self.ping_engine.ttls), 0)
        self.assertEqual(len(self.ping_engine.ping_times), 0)
        self.assertEqual(self.ping_engine.consecutive_failures, 0)
        self.assertEqual(self.ping_engine.outage_start_index, None)
        self.assertEqual(len(self.ping_engine.outage_history), 0)
    
    def test_get_statistics(self):
        """Test getting current statistics."""
        # Add some data first
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        stats = self.ping_engine.get_statistics()
        
        expected_keys = {
            'ttls', 'ping_times', 'failed_pings', 'total_pings',
            'failure_rate', 'outage_history', 'consecutive_failures', 'outage_start_index'
        }
        self.assertEqual(set(stats.keys()), expected_keys)
        self.assertEqual(stats['total_pings'], 2)
        self.assertEqual(stats['failed_pings'], 1)
        self.assertEqual(len(stats['ttls']), 2)
        self.assertEqual(len(stats['ping_times']), 2)
        self.assertEqual(stats['failure_rate'], 50.0)  # 1 failed out of 2 pings = 50%
    
    def test_max_points_limit(self):
        """Test that data is limited to max_points."""
        # Add more pings than max_points
        for i in range(self.ping_engine.max_points + 10):
            self.ping_engine._process_ping_result(ttl=i, ping_time=float(i))
        
        # Should only keep the last max_points
        self.assertEqual(len(self.ping_engine.ttls), self.ping_engine.max_points)
        self.assertEqual(len(self.ping_engine.ping_times), self.ping_engine.max_points)
        self.assertEqual(self.ping_engine.total_pings, self.ping_engine.max_points + 10)

    def test_failure_rate_calculation_empty_window(self):
        """Test failure rate calculation with empty sliding window."""
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['failure_rate'], 0.0)

    def test_failure_rate_calculation_all_successful(self):
        """Test failure rate calculation with all successful pings in window."""
        # Add 3 successful pings
        for i in range(3):
            self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['failure_rate'], 0.0)  # 0 failed out of 3 pings = 0%

    def test_failure_rate_calculation_all_failed(self):
        """Test failure rate calculation with all failed pings in window."""
        # Add 3 failed pings
        for i in range(3):
            self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['failure_rate'], 100.0)  # 3 failed out of 3 pings = 100%

    def test_failure_rate_calculation_mixed_results(self):
        """Test failure rate calculation with mixed successful and failed pings."""
        # Add 2 successful pings and 1 failed ping
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['failure_rate'], 33.33333333333333)  # 1 failed out of 3 pings ≈ 33.33%

    def test_failure_rate_calculation_sliding_window_behavior(self):
        """Test that failure rate reflects only the sliding window, not total history."""
        # Fill the window with successful pings
        for i in range(self.ping_engine.max_points):
            self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        # Verify 0% failure rate in window
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['failure_rate'], 0.0)
        self.assertEqual(stats['total_pings'], self.ping_engine.max_points)
        self.assertEqual(stats['failed_pings'], 0)
        
        # Add one failed ping to the end of the window
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Verify failure rate reflects only the window (1 failed out of 5 pings = 20%)
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['failure_rate'], 20.0)
        self.assertEqual(stats['total_pings'], self.ping_engine.max_points + 1)
        self.assertEqual(stats['failed_pings'], 1)

    def test_failure_rate_calculation_window_overflow(self):
        """Test failure rate calculation when window overflows and old data is removed."""
        # Fill the window with failed pings
        for i in range(self.ping_engine.max_points):
            self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Verify 100% failure rate in window
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['failure_rate'], 100.0)
        
        # Add successful pings to overflow the window
        for i in range(self.ping_engine.max_points):
            self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        # Verify failure rate reflects only the current window (0 failed out of 5 pings = 0%)
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['failure_rate'], 0.0)
        self.assertEqual(len(stats['ping_times']), self.ping_engine.max_points)


if __name__ == '__main__':
    unittest.main() 