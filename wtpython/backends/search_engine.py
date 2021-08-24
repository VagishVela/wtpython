from urllib.parse import urlencode

from wtpython.settings import SEARCH_ENGINE

from .trace import Trace


class SearchEngine:
    """Class for handling urls for search engines."""

    def __init__(self, trace: Trace, engine: str = SEARCH_ENGINE):
        self.query = trace.error
        self.engine = engine

    @property
    def url(self) -> str:
        """URL formatted for desired search engine."""
        endpoints = {
            "Google": "https://www.google.com/search?",
            "DuckDuckGo": "https://duckduckgo.com/?",
            "Yahoo": "https://search.yahoo.com/search?",
        }

        params = {"q": f"python {self.query}"}
        return endpoints[self.engine] + urlencode(params)
