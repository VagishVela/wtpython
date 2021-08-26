"""Default settings for wtpython."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_NAME = "WTPython"
GH_ISSUES = "https://github.com/what-the-python/wtpython/issues"

SO_MAX_RESULTS = 10
SEARCH_ENGINE = 'Google'

REQUEST_CACHE_LOCATION = Path.home() / Path(".wtpython_cache")
REQUEST_CACHE_DURATION = 60 * 60 * 24   # One day (in seconds)
