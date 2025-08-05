#!/usr/bin/env python3
"""Debug script to reproduce the outage detection bug."""

from ping_engine import PingEngine
from statistics import StatisticsCalculator

def main():
    # Test with the exact scenario: 4 consecutive failures in a large window
    engine = PingEngine(target="8.8.8.8", max_points=300)
    
    print("=== Reproducing the bug ===")
    
    # Add many successful pings to simulate the live scenario
    print("Adding 207 successful pings...")
    for i in range(207):
        engine._process_ping_result(ttl=64, ping_time=15.0)
    
    print("Adding 4 consecutive failures...")
    for i in range(4):
        engine._process_ping_result(ttl=None, ping_time=None)
        stats = engine.get_statistics()
        print(f"  After failure {i+1}: consecutive_failures={stats['consecutive_failures']}")
        print(f"    current_window_outages: {stats['current_window_outages']}")
    
    print("Adding success to end the outage...")
    engine._process_ping_result(ttl=64, ping_time=15.0)
    stats = engine.get_statistics()
    print(f"After ending outage:")
    print(f"  consecutive_failures: {stats['consecutive_failures']}")
    print(f"  current_window_outages: {stats['current_window_outages']}")
    
    # Calculate statistics
    calculated_stats = StatisticsCalculator.calculate_statistics(stats)
    print(f"  avg_outage_duration: {calculated_stats[4]}")
    
    # Add more successes to continue simulating
    print("Adding more successes...")
    for i in range(88):  # To reach index 299 like the live system
        engine._process_ping_result(ttl=64, ping_time=15.0)
    
    # Final check
    stats = engine.get_statistics()
    calculated_stats = StatisticsCalculator.calculate_statistics(stats)
    print(f"Final state:")
    print(f"  total_pings: {stats['total_pings']}")
    print(f"  window_size: {len(stats['ping_times'])}")
    print(f"  current_window_outages: {stats['current_window_outages']}")
    print(f"  avg_outage_duration: {calculated_stats[4]}")

if __name__ == "__main__":
    main()