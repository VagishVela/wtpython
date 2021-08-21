from __future__ import annotations

import argparse
import os.path
import runpy
import sys
import textwrap
from typing import Optional

import pyperclip
from rich import print

from wtpython.display import Display, store_results_in_module
from wtpython.no_display import dump_info
from wtpython.search_engine import SearchEngine
from wtpython.settings import SEARCH_ENGINE, SO_MAX_RESULTS
from wtpython.stackoverflow import StackOverflowFinder
from wtpython.trace import Trace


def run(args: list[str]) -> Optional[Exception]:
    """Execute desired program.

    This will set sys.argv as the desired program would receive them and execute the script.
    If there are no errors, the program will function just like using python, but formatted with Rich.
    If there are errors, this will return the exception object.
    """
    stashed, sys.argv = sys.argv, args
    exc = None
    try:
        runpy.run_path(args[0], run_name="__main__")
    except Exception as e:
        exc = e
    finally:
        sys.argv = stashed
    return exc


def parse_arguments() -> dict:
    """Parse arguments and store them in wtpython.arguments.args"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        additional information:
          wtpython acts as a substitute for python. Simply add `wt` to the beginning
          of the line and call your program with all the appropriate arguments:
                    $ wtpython [OPTIONS] <script.py> <arguments>"""),
    )

    parser.add_argument(
        "-n",
        "--no-display",
        action="store_true",
        default=False,
        help="Run without display",
    )
    parser.add_argument(
        "-c",
        "--copy-error",
        action="store_true",
        default=False,
        help="Copy error to clipboard",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        default=False,
        help="Clear StackOverflow cache",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments normally passed to wtpython",
    )

    opts = vars(parser.parse_args())

    if not opts['args']:
        parser.error("Please specify a script to run")
        sys.exit(1)

    if not os.path.isfile(opts['args'][0]):
        parser.error(f"{opts['args'][0]} is not a file")
        sys.exit(1)

    return opts


def main() -> None:
    """Run the application."""
    opts = parse_arguments()
    exc = run(opts['args'])

    if exc is None:  # No exceptions were raised by user's program
        return

    trace = Trace(exc)
    se = SearchEngine(exc, SEARCH_ENGINE)
    so = StackOverflowFinder(clear_cache=opts["clear_cache"])

    so_results = so.search(trace.error, SO_MAX_RESULTS)
    if len(so_results) == 0:
        # If no results have been found, search the error class name.
        so_results = so.search(trace.etype, SO_MAX_RESULTS)

    print(trace.rich_traceback)

    if opts["copy_error"]:
        pyperclip.copy(trace.error)

    if opts["no_display"]:
        dump_info(
            so_results=so_results,
            search_engine=se,
        )
    else:
        store_results_in_module(
            trace=trace,
            so_results=so_results,
            search_engine=se,
        )
        try:
            Display().run()
        except Exception as e:
            print(e)
