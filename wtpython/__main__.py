"""Main wtpython file.

This file parses the command line arguments, runs your program,
and then displays solutions for errors if they occur.
"""
from __future__ import annotations

import argparse
import os.path
import runpy
import sys
import textwrap
from typing import Optional

import pyperclip
from rich import print

from wtpython.backends import SearchEngine, StackOverflow, Trace
from wtpython.displays import TextualDisplay, dump_info
from wtpython.displays.textual_display import store_results_in_module


def run(args: list[str]) -> Optional[Trace]:
    """Execute desired program.

    This will set sys.argv as the desired program would receive it and executes the script.
    If there are no errors the program will function just like using Python but formatted with Rich.
    If there are errors this will return the exception object.

    Args:
        args: The arguments to pass to Python. args[0] should be the script to run.

    Returns:
        The exception object if there are errors, otherwise None.
    """
    stashed, sys.argv = sys.argv, args
    exc = None
    try:
        runpy.run_path(args[0], run_name="__main__")
    except Exception as e:
        exc = Trace(e)
    finally:
        sys.argv = stashed
    return exc


def parse_arguments() -> dict:
    """Parse sys.argv arguments.

    Args:
        None

    Returns:
        A dictionary of arguments.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
        Additional information:
          wtpython acts as a substitute for Python. Simply add `wt` to the beginning
          of the line and call your program with all the appropriate arguments:
                    $ wtpython [OPTIONS] <script.py> <arguments>"""
        ),
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

    if not opts["args"]:
        parser.error("Please specify a script to run")
        sys.exit(1)

    if not os.path.isfile(opts["args"][0]):
        parser.error(f"{opts['args'][0]} is not a file")
        sys.exit(1)

    return opts


def main() -> None:
    """Run the application.

    Args:
        None

    Returns:
        None
    """
    opts: dict = parse_arguments()
    trace: Optional[Trace] = run(opts["args"])

    if trace is None:  # No exceptions were raised by user's program
        return

    engine = SearchEngine(trace)
    so = StackOverflow.from_trace(trace=trace, clear_cache=opts["clear_cache"])

    print(trace.rich_traceback)

    if opts["copy_error"]:
        pyperclip.copy(trace.error)

    if opts["no_display"]:
        dump_info(
            so_results=so,
            search_engine=engine,
        )
    else:
        store_results_in_module(
            trace=trace,
            so_results=so,
            search_engine=engine,
        )
        try:
            TextualDisplay().run()
        except Exception as e:
            print(e)
