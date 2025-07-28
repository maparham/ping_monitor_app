"""Flask web application for ping monitoring."""

import json
import logging
import time
from flask import Flask, jsonify
from flask_cors import CORS
from .ping_engine import PingEngine
from .statistics import StatisticsCalculator
from .config import DEFAULT_TARGET, DEFAULT_MAX_POINTS, DEFAULT_NUM_WINDOWS, AUTO_REFRESH_INTERVAL, DEFAULT_HOST, DEFAULT_PORT

logging.getLogger('werkzeug').setLevel(logging.ERROR)

def create_app(target: str = DEFAULT_TARGET, max_points: int = DEFAULT_MAX_POINTS, num_windows: int = DEFAULT_NUM_WINDOWS, auto_refresh_interval: int = AUTO_REFRESH_INTERVAL, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> Flask:
    """Create Flask application."""
    app = Flask(__name__)
    CORS(app)
    
    ping_engine = PingEngine(target=target, max_points=max_points, num_windows=num_windows)
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Network Monitor API',
            'endpoints': {
                'GET /api/data': 'Get network data',
                'POST /api/reset': 'Reset statistics'
            }
        })
    
    @app.route('/api/data')
    def api_data():
        """Get current network data."""
        try:
            stats_data = ping_engine.get_statistics()
            ttls, ping_times = stats_data['ttls'], stats_data['ping_times']
            
            # Transform data for Recharts format
            chart_data = []
            for i, (ttl, ping_time) in enumerate(zip(ttls, ping_times)):
                if ttl is not None and ping_time is not None:
                    chart_data.append({
                        'index': i,
                        'ttl': ttl,
                        'pingTime': ping_time,
                        'timestamp': time.time()
                    })
                else:
                    # Failed pings - mark with null values
                    chart_data.append({
                        'index': i,
                        'ttl': None,
                        'pingTime': None,
                        'timestamp': time.time()
                    })
            
            failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failed_pings = \
                StatisticsCalculator.calculate_statistics(stats_data, num_windows=num_windows)
            
            return jsonify({
                'chart_data': chart_data,
                'failure_rate': failure_rate,
                'avg_ping_time': avg_ping_time,
                'min_ping_time': min_ping_time,
                'max_ping_time': max_ping_time,
                'avg_failed_pings': avg_failed_pings,
                'total_pings': stats_data.get('total_pings', 0)
            })
        except Exception as e:
            logging.error(f"Error serving API data: {e}")
            return jsonify({
                'chart_data': [],
                'failure_rate': 0.0,
                'avg_ping_time': None,
                'min_ping_time': None,
                'max_ping_time': None,
                'avg_failed_pings': 0.0,
                'total_pings': 0
            }), 500

    @app.route('/api/config')
    def api_config():
        """Get configuration data."""
        try:
            return jsonify({
                'max_points': max_points,
                'num_windows': num_windows,
                'target': target,
                'auto_refresh_interval': auto_refresh_interval,
                'api_url': f'http://{host}:{port}'
            })
        except Exception as e:
            logging.error(f"Error serving config data: {e}")
            return jsonify({
                'max_points': DEFAULT_MAX_POINTS,
                'num_windows': DEFAULT_NUM_WINDOWS,
                'target': DEFAULT_TARGET,
                'auto_refresh_interval': AUTO_REFRESH_INTERVAL,
                'api_url': f'http://{DEFAULT_HOST}:{DEFAULT_PORT}'
            }), 500
    
    @app.route('/api/reset', methods=['POST'])
    def api_reset():
        """Reset all statistics."""
        try:
            ping_engine.reset()
            return jsonify({'message': 'Statistics reset successfully'})
        except Exception as e:
            logging.error(f"Error resetting statistics: {e}")
            return jsonify({'error': 'Failed to reset statistics'}), 500
    
    @app.before_request
    def start_ping_engine():
        """Start ping engine before request."""
        if not ping_engine.is_running():
            ping_engine.start()
    
    return app 