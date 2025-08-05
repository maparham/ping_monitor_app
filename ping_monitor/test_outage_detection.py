"""Tests for outage detection functionality."""

import unittest
from ping_engine import PingEngine

class TestOutageDetection(unittest.TestCase):
    """Test cases for outage detection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.ping_engine = PingEngine(target="8.8.8.8", max_points=10)

    def tearDown(self):
        """Clean up after tests."""
        if self.ping_engine.is_running():
            self.ping_engine.stop()

    def test_single_failure_not_outage(self):
        """Test that a single failure is not considered an outage."""
        # Single failure
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [])
        self.assertEqual(stats['consecutive_failures'], 1)

    def test_two_consecutive_failures_outage(self):
        """Test that two consecutive failures create an outage."""
        # Two consecutive failures
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # No outage recorded yet (need successful ping to end it)
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [])
        self.assertEqual(stats['consecutive_failures'], 2)
        
        # Successful ping should record the outage
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [2])
        self.assertEqual(stats['consecutive_failures'], 0)

    def test_three_consecutive_failures_outage(self):
        """Test that three consecutive failures create an outage."""
        # Three consecutive failures
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # No outage recorded yet (need successful ping to end it)
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [])
        self.assertEqual(stats['consecutive_failures'], 3)
        
        # Successful ping should record the outage
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [3])
        self.assertEqual(stats['consecutive_failures'], 0)

    def test_multiple_outages_in_window(self):
        """Test multiple outages in the same window."""
        # First outage: 2 failures
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)  # End first outage
        
        # Second outage: 3 failures
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)  # End second outage
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(len(stats['outage_history']), 2)
        self.assertIn(2, stats['outage_history'])
        self.assertIn(3, stats['outage_history'])

    def test_outage_spanning_window_boundary(self):
        """Test outage that spans across window boundaries."""
        # Fill window with failures
        for i in range(8):
            self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Add 2 more failures to trigger outage
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Add successful ping to end outage
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(len(stats['outage_history']), 1)
        self.assertEqual(stats['outage_history'][0], 10)  # All 10 pings were failures
        self.assertEqual(stats['outage_start_index'], None)  # Should be reset

    def test_outage_ending_at_window_boundary(self):
        """Test outage that ends exactly at window boundary."""
        # Add 9 successful pings
        for i in range(9):
            self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        # Add 2 failures to create outage
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Add successful ping to end outage
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(len(stats['outage_history']), 1)
        self.assertEqual(stats['outage_history'][0], 2)

    def test_interrupted_outage(self):
        """Test outage that is interrupted by a successful ping."""
        # Start with 2 failures
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Interrupt with successful ping
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        # Start another outage
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(len(stats['outage_history']), 2)
        self.assertEqual(stats['outage_history'][0], 2)
        self.assertEqual(stats['outage_history'][1], 2)

    def test_no_outages_in_window(self):
        """Test window with no outages."""
        # Add only successful pings
        for i in range(10):
            self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [])
        self.assertEqual(stats['consecutive_failures'], 0)

    def test_reset_clears_outages(self):
        """Test that reset clears all outage data."""
        # Create an outage
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        # Verify outage was recorded
        stats = self.ping_engine.get_statistics()
        self.assertEqual(len(stats['outage_history']), 1)
        
        # Reset
        self.ping_engine.reset()
        
        # Verify outage data is cleared
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [])
        self.assertEqual(stats['consecutive_failures'], 0)
        self.assertEqual(stats['outage_start_index'], None)

    def test_statistics_calculation_with_outages(self):
        """Test statistics calculation with various outage scenarios."""
        # Create multiple outages
        for i in range(3):
            # 2 failures
            self.ping_engine._process_ping_result(ttl=None, ping_time=None)
            self.ping_engine._process_ping_result(ttl=None, ping_time=None)
            # End with success
            self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        
        # Should have 3 outages, each with duration 2
        self.assertEqual(len(stats['outage_history']), 3)
        self.assertEqual(stats['outage_history'], [2, 2, 2])
        
        # Total pings: 9 (3 outages * 3 pings each)
        self.assertEqual(stats['total_pings'], 9)
        # Failed pings: 6 (3 outages * 2 failures each)
        self.assertEqual(stats['failed_pings'], 6)


if __name__ == '__main__':
    unittest.main() 