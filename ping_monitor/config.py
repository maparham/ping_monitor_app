"""
Configuration Module
Centralized configuration constants for the ping monitor application.
"""

# Ping Engine Configuration
PING_TIMEOUT = 1
PING_INTERVAL = 1
DEFAULT_TARGET = "8.8.8.8"
DEFAULT_MAX_POINTS = 60

# Data Constants
DEFAULT_TTL = 119
DEFAULT_PING_TIME = 10

# Web Application Configuration
DEFAULT_PORT = 5000
DEFAULT_HOST = "0.0.0.0"
AUTO_REFRESH_INTERVAL = 1  # seconds

# Chart Configuration
DEFAULT_CHART_HEIGHT = 800
DEFAULT_Y_PADDING_FACTOR = 0.1
DEFAULT_TTL_RANGE = (115, 125)
DEFAULT_PING_RANGE = (0, 100)
DEFAULT_MAX_CHART_POINTS = 59

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 