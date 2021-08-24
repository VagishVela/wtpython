from requests_cache import CachedSession
from requests_cache.backends import FileCache

from wtpython.settings import REQUEST_CACHE_DURATION, REQUEST_CACHE_LOCATION


class CachedResponse:
    """Class for caching web queries.

    This class should be extended by any class that makes web queries.
    The `cache_key` should be defined to avoid caching conflicts.
    """

    cache_key = 'wtpython'

    def __init__(self, clear_cache: bool = False) -> None:
        """Initialize the session and cache."""
        self.session = CachedSession(
            self.cache_key,
            backend=FileCache(REQUEST_CACHE_LOCATION),
            expire_after=REQUEST_CACHE_DURATION,
        )
        if clear_cache:
            self.session.cache.clear()

    def __del__(self) -> None:
        """Close the session on exit."""
        self.session.close()
