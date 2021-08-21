"""wtpython"""
from rich import print
from rich.markdown import HorizontalRule

from wtpython.settings import GH_ISSUES

__version__ = "0.1"


class WTPythonError(Exception):
    """Generic Error for wtpython."""

    def __del__(self) -> None:
        print(HorizontalRule())
        print("[red]We're terribly sorry, but wtpython has encountered an issue.")
        print(
            "[bold][green]Please let us know by by opening a new issue at:"
            f"[/] [link={GH_ISSUES}]{GH_ISSUES}[/link]\n"
        )


class SearchError(WTPythonError):
    """Custom Error for Searching for External Data."""
