import argparse
import runpy
import sys
import traceback

import pyperclip
from rich import print

from wtpython import SearchError
from wtpython.backends.stackoverflow import StackOverflowFinder
from wtpython.display import Display, store_results_in_module
from wtpython.settings import MAX_SO_RESULTS


def parse_arguments() -> tuple[dict, list]:
    """Parse arguments and store them in wtpython.arguments.args"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--no-display",
        action='store_true',
        default=False,
        help="Run without display"
    )
    parser.add_argument(
        "-c",
        "--copy-error",
        action='store_true',
        default=False,
        help="Copy error to clipboard",
    )

    flags, args = parser.parse_known_args()

    # Set sys.argv as the intended script would receive them
    sys.argv = ['python', *args[1:]]
    return vars(flags), args


def main() -> None:
    """Run the application"""
    flags, args = parse_arguments()
    exc = None

    try:
        runpy.run_path(args[0], run_name='__main__')
    except Exception as e:
        exc = e

    error = ''.join(traceback.format_exception_only(type(exc), exc)).strip()
    so = StackOverflowFinder()
    try:
        so_results = so.search(error, MAX_SO_RESULTS)
    except SearchError as e:
        print(e)
        return

    if flags["copy_error"]:
        pyperclip.copy(error)

    if flags['no_display']:
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        print(so_results)
    else:
        store_results_in_module(exc, so_results)
        Display().run()


if __name__ == "__main__":
    main()
