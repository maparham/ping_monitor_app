"""Configuration for the ping monitor."""

# Ping settings
PING_TIMEOUT = 1
PING_INTERVAL = 1
DEFAULT_TARGET = "8.8.8.8"
DEFAULT_MAX_POINTS = 300

# Statistics settings
DEFAULT_NUM_WINDOWS = 3  # Number of windows to use for avg_failed_pings calculation

# Web settings
DEFAULT_PORT = 5000
DEFAULT_HOST = "0.0.0.0"
AUTO_REFRESH_INTERVAL = 1 