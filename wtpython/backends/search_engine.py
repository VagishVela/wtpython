"""Manages data relevant to search engines."""
from urllib.parse import urlencode

from wtpython.settings import SEARCH_ENGINE

from .trace import Trace


class SearchEngine:
    """Class for handling urls for search engines."""

    def __init__(self, trace: Trace, engine: str = SEARCH_ENGINE) -> None:
        """Search engine object.

        Args:
            trace: wtpython trace object.
            engine: search engine to use.

        Returns:
            SearchEngine object.
        """
        self.query = trace.error
        self.engine = engine

    @property
    def url(self) -> str:
        """Url formatted for desired search engine."""
        endpoints = {
            "Google": "https://www.google.com/search?",
            "DuckDuckGo": "https://duckduckgo.com/?",
            "Yahoo": "https://search.yahoo.com/search?",
        }

        params = {"q": f"python {self.query}"}
        return endpoints[self.engine] + urlencode(params)
