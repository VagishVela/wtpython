from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_NAME = "WTPython"

# https://api.stackexchange.com/docs/filters, chooses what fields to be included or excluded.
# For example, if getting the user isn't needed, a specific filter can be created to
# not include the user field. This decreases API calls to save bandwidth.
# This is the filter we used: https://api.stackexchange.com/2.3/filters/!6VvPDzQ)xXOrL
# To create a custom filter, use https://api.stackexchange.com/docs/create-filter
SO_FILTER = "!6VvPDzQ)xXOrL"
SO_MAX_RESULTS = 10
SO_API = "https://api.stackexchange.com/2.3"
SEARCH_ENGINE = 'Google'

REQUEST_CACHE_LOCATION = Path.home() / Path(".wtpython_cache")
REQUEST_CACHE_DURATION = 60 * 60 * 24   # One day (in seconds)

GH_ORG = "what-the-python"
GH_REPO = "wtpython"
GH_ISSUES = f"https://github.com/{GH_ORG}/{GH_REPO}/issues"
