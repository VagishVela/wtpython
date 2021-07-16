import argparse
import runpy
import sys
import traceback

import pyperclip
from rich import print

from wtpython import SearchError
from wtpython.backends.stackoverflow import StackOverflowFinder
from wtpython.display import Display, store_results_in_module
from wtpython.settings import GH_ISSUES, MAX_SO_RESULTS


def run(args: list[str]) -> Exception:
    """Execute desired program."""
    # Set sys.argv as the intended script would receive them
    stashed, sys.argv = sys.argv, args
    exc = None
    try:
        runpy.run_path(args[0], run_name='__main__')
    except Exception as e:
        exc = e
    finally:
        sys.argv = stashed
    return exc


def display_app_error(exc: Exception) -> None:
    """Display error message and request user to report an issue."""
    print(":cry: We're terribly sorry, but our app has encounterd an issue.")
    print("-" * 80)
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    print("-" * 80)
    print(f":nerd_face: Please let us know by by opening a new issue at {GH_ISSUES}")


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

    return vars(flags), args


def main() -> None:
    """Run the application"""
    flags, args = parse_arguments()
    exc = run(args)

    if exc is None:
        return

    error = ''.join(traceback.format_exception_only(type(exc), exc)).strip()

    if flags["copy_error"]:
        pyperclip.copy(error)

    so = StackOverflowFinder()
    try:
        so_results = so.search(error, MAX_SO_RESULTS)
    except SearchError as e:
        display_app_error(e)
        return

    if flags['no_display']:
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        print(so_results)
    else:
        store_results_in_module(exc, so_results)
        try:
            Display().run()
        except Exception as e:
            display_app_error(e)
            return


if __name__ == "__main__":
    main()
