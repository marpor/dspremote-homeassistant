"""Constants for the dspremote integration."""

from datetime import timedelta

DOMAIN = "dspremote"
PLATFORMS = ["number", "select", "switch", "sensor", "button"]

CONF_BASE_URL = "base_url"
CONF_USE_WEBSOCKET = "use_websocket"
CONF_PREFIX = "prefix"
CONF_SELECTED_PATHS = "selected_paths"
CONF_ADDITIONAL_PATH_PATTERNS = "additional_path_patterns"

DEFAULT_USE_WEBSOCKET = True
DEFAULT_PREFIX = "/"
DEFAULT_SELECTED_PATHS: list[str] = []
DEFAULT_SCAN_INTERVAL = timedelta(seconds=10)

