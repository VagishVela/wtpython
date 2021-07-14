from pathlib import Path

REQUEST_CACHE_LOCATION = Path.home() / Path(".wtpython_cache")
REQUEST_CACHE_DURATION = 60 * 60 * 24   # One day (in seconds)
