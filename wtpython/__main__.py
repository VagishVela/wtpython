import argparse

import pyperclip
from rich import print

from wtpython import SearchError
from wtpython.backends.stackoverflow import StackOverflowFinder
from wtpython.core import parse_traceback, run_and_get_stderr
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
        help="Run without display",
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
    tb = run_and_get_stderr(args)
    if not tb:
        return

    parsed_tb = parse_traceback(tb)

    so = StackOverflowFinder()
    try:
        so_results = so.search(parsed_tb["error_message"], MAX_SO_RESULTS)
    except SearchError as e:
        print(e)
        return

    store_results_in_module(parsed_tb, so_results)

    if flags["copy_error"]:
        pyperclip.copy(parsed_tb["error_message"])

    if flags['no_display']:
        print(parsed_tb)
        print(so_results)
    else:
        Display().run()


if __name__ == "__main__":
    main()
