from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_NAME = "WTPython"
SO_FILTER = "!6VvPDzQ)xXOrL"  # https://api.stackexchange.com/docs/filters
SO_MAX_RESULTS = 10
SO_API = "https://api.stackexchange.com/2.3"

REQUEST_CACHE_LOCATION = Path.home() / Path(".wtpython_cache")
REQUEST_CACHE_DURATION = 60 * 60 * 24   # One day (in seconds)

GH_ORG = "what-the-python"
GH_REPO = "wtpython"
GH_ISSUES = f"https://github.com/{GH_ORG}/{GH_REPO}/issues"
