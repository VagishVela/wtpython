from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_NAME = "WTPython"
SO_FILTER = "!6VvPDzQ)xXOrL"  # https://api.stackexchange.com/docs/filters
SO_MAX_RESULTS = 10
SO_API = "https://api.stackexchange.com/2.3"

GH_ORG = "what-the-python"
GH_REPO = "wtpython"
GH_ISSUES = f"https://github.com/{GH_ORG}/{GH_REPO}/issues"
