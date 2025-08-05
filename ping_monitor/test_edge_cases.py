"""Tests for edge cases in ping monitoring."""

import unittest
import random
from ping_engine import PingEngine

class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and boundary conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.ping_engine = PingEngine(target="8.8.8.8", max_points=10)

    def tearDown(self):
        """Clean up after tests."""
        if self.ping_engine.is_running():
            self.ping_engine.stop()

    def test_small_window_two_failures(self):
        """Window of size 2 should still detect and record a 2-failure outage correctly."""
        small_engine = PingEngine(target="8.8.8.8", max_points=2)
        
        # Add two failures
        small_engine._process_ping_result(ttl=None, ping_time=None)
        small_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Add successful ping to end outage
        small_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = small_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [2])  # Should record the outage
        self.assertEqual(stats['consecutive_failures'], 0)

    def test_reset_during_ongoing_outage(self):
        """Calling reset while an outage is in progress should clear all counters."""
        # Start an outage
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Verify outage is in progress
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['consecutive_failures'], 2)
        self.assertIsNotNone(stats['outage_start_index'])
        
        # Reset during outage
        self.ping_engine.reset()
        
        # Verify all counters are cleared
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['outage_history'], [])
        self.assertEqual(stats['consecutive_failures'], 0)
        self.assertEqual(stats['outage_start_index'], None)

    def test_long_spanning_outage_multiple_windows(self):
        """Test an outage that spans multiple complete windows."""
        # Fill first window with failures
        for i in range(10):
            self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Add 2 more failures to continue outage
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Add successful ping to end outage
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(len(stats['outage_history']), 1)
        self.assertEqual(stats['outage_history'][0], 12)  # All 12 pings were failures

    def test_window_filled_with_successes_after_outage(self):
        """Test that a window filled with successes after an outage resets properly."""
        # Create an outage
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        # Fill window with successes
        for i in range(10):
            self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(len(stats['outage_history']), 0)  # Outage should be removed as window slides
        self.assertEqual(stats['consecutive_failures'], 0)

    def test_consecutive_failure_counter_across_windows(self):
        """Test that consecutive_failures is maintained correctly across window boundaries."""
        # Fill window with failures
        for i in range(10):
            self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        # Add one more failure
        self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['consecutive_failures'], 11)
        
        # Add successful ping to end outage
        self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
        
        stats = self.ping_engine.get_statistics()
        self.assertEqual(stats['consecutive_failures'], 0)

    def test_stress_random_pattern(self):
        """Stress test with many random successes/failures to verify invariants."""
        random.seed(42)  # For reproducible results
        
        # Generate 100 random pings
        for i in range(100):
            if random.random() < 0.8:  # 80% success rate
                self.ping_engine._process_ping_result(ttl=64, ping_time=15.2)
            else:
                self.ping_engine._process_ping_result(ttl=None, ping_time=None)
        
        stats = self.ping_engine.get_statistics()
        
        # Verify basic invariants
        self.assertEqual(stats['total_pings'], 100)
        self.assertGreaterEqual(stats['failed_pings'], 0)
        self.assertLessEqual(stats['failed_pings'], 100)
        
        # Verify outage history contains only valid durations
        for duration in stats['outage_history']:
            self.assertGreaterEqual(duration, 2)
        
        # Verify consecutive failures is reasonable
        self.assertGreaterEqual(stats['consecutive_failures'], 0)

    def test_multiple_window_sizes(self):
        """Test the same outage pattern with different window sizes."""
        window_sizes = [4, 5, 10]
        
        for window_size in window_sizes:
            with self.subTest(window_size=window_size):
                engine = PingEngine(target="8.8.8.8", max_points=window_size)
                
                # Create an outage
                engine._process_ping_result(ttl=None, ping_time=None)
                engine._process_ping_result(ttl=None, ping_time=None)
                engine._process_ping_result(ttl=64, ping_time=15.2)
                
                stats = engine.get_statistics()
                self.assertEqual(len(stats['outage_history']), 1)
                self.assertEqual(stats['outage_history'][0], 2)


if __name__ == '__main__':
    unittest.main()
