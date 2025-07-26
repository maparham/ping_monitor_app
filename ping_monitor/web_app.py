"""
Web App Module
Handles Flask application and web routes.
"""

import json
import logging
import plotly.utils
from flask import Flask, render_template_string
from .ping_engine import PingEngine
from .statistics import StatisticsCalculator
from .plot_generator import PlotGenerator
from .templates import HTML_TEMPLATE
from .config import DEFAULT_TARGET, DEFAULT_MAX_POINTS, LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def create_app(target: str = DEFAULT_TARGET, max_points: int = DEFAULT_MAX_POINTS) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        target: IP address to ping
        max_points: Maximum number of data points to store
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Initialize ping engine
    ping_engine = PingEngine(target=target, max_points=max_points)
    
    @app.route('/')
    def index():
        """Serve the main page with the plot and statistics."""
        try:
            # Get current data (may contain None values for failed pings)
            ttls, ping_times = ping_engine.get_data()
            stats_data = ping_engine.get_statistics()
            
            # Create plot with target IP
            fig = PlotGenerator.create_plot(ttls, ping_times, target=target)
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Calculate statistics
            failure_rate, avg_ping_time, min_ping_time, max_ping_time, avg_failure_duration = \
                StatisticsCalculator.calculate_statistics(stats_data)
            
            return render_template_string(HTML_TEMPLATE, 
                                        plot_json=plot_json,
                                        failure_rate=failure_rate,
                                        avg_ping_time=avg_ping_time,
                                        min_ping_time=min_ping_time,
                                        max_ping_time=max_ping_time,
                                        avg_failure_duration=avg_failure_duration,
                                        total_pings=stats_data.get('total_pings', 0))
        except Exception as e:
            logger.error(f"Error serving index page: {e}")
            # Return a basic error page
            return render_template_string(HTML_TEMPLATE, 
                                        plot_json='{"data":[], "layout":{"title":"Error loading data"}}',
                                        failure_rate=0.0,
                                        avg_ping_time=0.0,
                                        min_ping_time=0.0,
                                        max_ping_time=0.0,
                                        avg_failure_duration=0.0,
                                        total_pings=0)
    
    @app.before_request
    def start_ping_engine():
        """Start the ping engine before each request (only if not already started)."""
        try:
            if not ping_engine.running:
                ping_engine.start()
        except Exception as e:
            logger.error(f"Error starting ping engine: {e}")
    
    @app.teardown_appcontext
    def stop_ping_engine(exception=None):
        """Stop the ping engine when the app context is torn down."""
        try:
            ping_engine.stop()
        except Exception as e:
            logger.error(f"Error stopping ping engine: {e}")
    
    logger.info(f"Flask app created for target: {target}")
    return app 