"""Unit tests for ping_engine module."""

import unittest
from unittest.mock import patch, MagicMock
import time
import threading
from ping_monitor.ping_engine import PingEngine
from ping_monitor.config import DEFAULT_TARGET, DEFAULT_MAX_POINTS, DEFAULT_NUM_WINDOWS


class TestPingEngine(unittest.TestCase):
    """Test cases for PingEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ping_engine = PingEngine()
    
    def tearDown(self):
        """Clean up after tests."""
        if self.ping_engine.is_running():
            self.ping_engine.stop()
    
    def test_initialization(self):
        """Test PingEngine initialization."""
        self.assertEqual(self.ping_engine.target, DEFAULT_TARGET)
        self.assertEqual(self.ping_engine.max_points, DEFAULT_MAX_POINTS)
        self.assertEqual(self.ping_engine.num_windows, DEFAULT_NUM_WINDOWS)
        self.assertFalse(self.ping_engine.is_running())
        self.assertEqual(self.ping_engine.failed_pings, 0)
        self.assertEqual(self.ping_engine.total_pings, 0)
    
    def test_initialization_with_custom_params(self):
        """Test PingEngine initialization with custom parameters."""
        custom_engine = PingEngine(
            target="1.1.1.1",
            max_points=20,
            num_windows=5
        )
        self.assertEqual(custom_engine.target, "1.1.1.1")
        self.assertEqual(custom_engine.max_points, 20)
        self.assertEqual(custom_engine.num_windows, 5)
    
    @patch('ping_monitor.ping_engine.subprocess.run')
    def test_ping_target_success(self, mock_run):
        """Test successful ping operation."""
        # Mock successful ping response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "64 bytes from 8.8.8.8: icmp_seq=1 ttl=113 time=15.2 ms"
        mock_run.return_value = mock_result
        
        ttl, ping_time = self.ping_engine.ping_target()
        
        self.assertEqual(ttl, 113)
        self.assertEqual(ping_time, 15.2)
        mock_run.assert_called_once()
    
    @patch('ping_monitor.ping_engine.subprocess.run')
    def test_ping_target_failure(self, mock_run):
        """Test failed ping operation."""
        # Mock failed ping response
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        ttl, ping_time = self.ping_engine.ping_target()
        
        self.assertIsNone(ttl)
        self.assertIsNone(ping_time)
    
    @patch('ping_monitor.ping_engine.subprocess.run')
    def test_ping_target_timeout(self, mock_run):
        """Test ping operation with timeout."""
        mock_run.side_effect = TimeoutError("Command timed out")
        
        ttl, ping_time = self.ping_engine.ping_target()
        
        self.assertIsNone(ttl)
        self.assertIsNone(ping_time)
    
    @patch('ping_monitor.ping_engine.subprocess.run')
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
    
    def test_process_ping_result_window_tracking(self):
        """Test window-based tracking of failed pings."""
        # Process enough pings to complete a window
        for i in range(self.ping_engine.max_points):
            self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Check that window data was stored
        self.assertEqual(len(self.ping_engine.failed_pings_per_window), 1)
        self.assertEqual(self.ping_engine.failed_pings_per_window[0], self.ping_engine.max_points)
        self.assertEqual(self.ping_engine.current_window_failed, 0)
        self.assertEqual(self.ping_engine.current_window_total, 0)
    
    def test_start_stop(self):
        """Test starting and stopping the ping engine."""
        self.assertFalse(self.ping_engine.is_running())
        
        self.ping_engine.start()
        self.assertTrue(self.ping_engine.is_running())
        self.assertIsInstance(self.ping_engine.ping_thread, threading.Thread)
        
        self.ping_engine.stop()
        self.assertFalse(self.ping_engine.is_running())
    
    def test_reset(self):
        """Test resetting all statistics."""
        # Add some data first
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Verify data exists
        self.assertEqual(self.ping_engine.total_pings, 2)
        self.assertEqual(self.ping_engine.failed_pings, 1)
        self.assertEqual(len(self.ping_engine.ttls), 2)
        
        # Reset
        self.ping_engine.reset()
        
        # Verify reset
        self.assertEqual(self.ping_engine.total_pings, 0)
        self.assertEqual(self.ping_engine.failed_pings, 0)
        self.assertEqual(len(self.ping_engine.ttls), 0)
        self.assertEqual(len(self.ping_engine.ping_times), 0)
        self.assertEqual(len(self.ping_engine.failed_pings_per_window), 0)
        self.assertEqual(self.ping_engine.current_window_failed, 0)
        self.assertEqual(self.ping_engine.current_window_total, 0)
    
    def test_get_statistics(self):
        """Test getting current statistics."""
        # Add some data
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        stats = self.ping_engine.get_statistics()
        
        expected_keys = {
            'ttls', 'ping_times', 'failed_pings', 'total_pings',
            'failed_pings_per_window', 'current_window_failed', 'current_window_total'
        }
        self.assertEqual(set(stats.keys()), expected_keys)
        self.assertEqual(stats['total_pings'], 2)
        self.assertEqual(stats['failed_pings'], 1)
        self.assertEqual(len(stats['ttls']), 2)
        self.assertEqual(len(stats['ping_times']), 2)
    
    def test_max_points_limit(self):
        """Test that data is limited to max_points."""
        # Add more data than max_points
        for i in range(self.ping_engine.max_points + 5):
            self.ping_engine._process_ping_result(ttl=64 + i, ping_time=15.2 + i)
        
        # Verify only max_points are kept
        self.assertEqual(len(self.ping_engine.ttls), self.ping_engine.max_points)
        self.assertEqual(len(self.ping_engine.ping_times), self.ping_engine.max_points)
        
        # Verify oldest data was removed (FIFO behavior)
        self.assertEqual(self.ping_engine.ttls[0], 64 + 5)  # First item should be the 6th added
        self.assertEqual(self.ping_engine.ping_times[0], 15.2 + 5)


if __name__ == '__main__':
    unittest.main() 