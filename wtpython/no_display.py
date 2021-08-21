"""
This module works to dump the information for the no-display option.

Each datasource should have it's own function while `dump_info` will
control the order in which they are displayed.
"""
from rich import print
from rich.markdown import HorizontalRule

from wtpython.stackoverflow import StackOverflowQuestion


def dump_stackoverflow(so_results: list[StackOverflowQuestion]) -> None:
    """Dump Stackoverflow Questions list."""
    print("[yellow]Stack Overflow Results:[/]\n")
    print("\n\n".join([
        f"{i}. {result}"
        for i, result
        in enumerate(so_results, 1)
    ]))


def dump_info(so_results: list[StackOverflowQuestion]) -> None:
    """Dump information for no-display mode.

    The traceback message is dumped before display vs no-display is evaluated.
    """
    print(HorizontalRule())
    dump_stackoverflow(so_results)
