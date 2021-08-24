"""
This module works to dump the information for the no-display option.

Each datasource should have it's own function while `dump_info` will
control the order in which they are displayed.
"""
from rich import print
from rich.markdown import HorizontalRule

from wtpython.backends import SearchEngine, StackOverflow
from wtpython.settings import SEARCH_ENGINE


def _header(txt: str) -> str:
    """Format header for section.

    Args:
        txt: Text to display in header.

    Returns:
        Formatted header.
    """
    print(HorizontalRule())
    return f"[yellow]{txt}:[/]\n"


def _stackoverflow(so: StackOverflow) -> None:
    """Dump Stackoverflow Questions list.

    Args:
        so: Stackoverflow object.

    Returns:
        None
    """
    print(_header("Stack Overflow Results"))
    print(so.no_display())


def _searchengine(search_engine: SearchEngine) -> None:
    """Dump url for search engine.

    Args:
        search_engine: SearchEngine object.

    Returns:
        None
    """
    print(_header(f"Search on {SEARCH_ENGINE}"))
    print(search_engine.url)


def dump_info(so_results: StackOverflow, search_engine: SearchEngine) -> None:
    """Dump information for no-display mode.

    The traceback message is dumped before display vs no-display is evaluated.

    Args:
        so_results: Stackoverflow object.
        search_engine: SearchEngine object.

    Returns:
        None
    """
    _stackoverflow(so_results)
    _searchengine(search_engine)
    print()
