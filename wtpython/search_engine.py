import traceback
from urllib.parse import urlencode


class SearchEngine:
    """Class for handling urls for search engines."""

    def __init__(self, exc: Exception, engine: str):
        self.query = "".join(
            traceback.format_exception_only(type(exc), exc)
        ).strip()
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
