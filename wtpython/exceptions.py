from rich import print
from rich.markdown import HorizontalRule

from wtpython.formatters import rich_link
from wtpython.settings import GH_ISSUES


class WTPythonError(Exception):
    """Generic Error for wtpython.

    For any internal application error, this will surround the traceback
    with horizontal rules and print a message to the user.
    """

    def __init__(self, *args) -> None:
        print(HorizontalRule())
        super().__init__(*args)

    def __del__(self) -> None:
        print(HorizontalRule())
        print("[red]We're terribly sorry, but wtpython has encountered an issue.")
        print(
            "[bold][green]Please let us know by by opening a new issue at:[/]"
            f"{rich_link(GH_ISSUES)}"
        )
        print("Please include the information between the horizontal rules above.")


class SearchError(WTPythonError):
    """Custom Error for Searching for External Data."""
