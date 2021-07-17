import argparse
import runpy
import sys
import textwrap
import traceback
from pathlib import Path

import pyperclip
from rich import print
from rich.markdown import HorizontalRule
from rich.traceback import Traceback

from wtpython import SearchError
from wtpython.display import Display, store_results_in_module
from wtpython.settings import GH_ISSUES, SO_MAX_RESULTS
from wtpython.stackoverflow import StackOverflowFinder


def trim_exception_traceback(tb: traceback) -> traceback:
    """
    Trim the traceback to remove extra frames

    Because of the way we are currently running the code, any traceback
    created during the execution of the application will be include the
    stack frames of this application. This function removes all the stack
    frames from the beginning of the traceback until we stop seeing `runpy`.
    """
    seen_runpy = False
    while tb is not None:
        cur = tb.tb_frame
        filename = Path(cur.f_code.co_filename).name
        if filename == "runpy.py":
            seen_runpy = True
        elif seen_runpy and filename != "runpy.py":
            break
        tb = tb.tb_next

    return tb


def run(args: list[str]) -> Exception:
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
        exc.__traceback__ = trim_exception_traceback(exc.__traceback__)
    finally:
        sys.argv = stashed
    return exc


def display_app_error(exc: Exception) -> None:
    """Display error message and request user to report an issue.

    This should only occur if this app has an internal issue.
    """
    print(":cry: [red]We're terribly sorry, but our app has encountered an issue.")
    print(HorizontalRule())
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    print(HorizontalRule())
    print(
        f":nerd_face: [bold][green]Please let us know by by opening a new issue at:[/] [blue underline]{GH_ISSUES}"
    )


def parse_arguments() -> tuple[dict, list]:
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

    flags, args = parser.parse_known_args()
    if not args:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return vars(flags), args


def main() -> None:
    """Run the application."""
    flags, args = parse_arguments()
    exc = run(args)

    if exc is None:  # No exceptions were raised by user's program
        return

    error = "".join(traceback.format_exception_only(type(exc), exc)).strip()
    error_lines = error.split("\n")
    if len(error_lines) > 1:
        error = error_lines[-1]

    if flags["copy_error"]:
        pyperclip.copy(error)

    so = StackOverflowFinder(clear_cache=flags["clear_cache"])

    try:
        so_results = so.search(error, SO_MAX_RESULTS)
    except SearchError as e:
        display_app_error(e)
        return

    print(Traceback.from_exception(type(exc), exc, exc.__traceback__))
    if flags["no_display"]:
        print(HorizontalRule())
        print("[yellow]Stack Overflow Results:[/]\n")
        print("\n\n".join([
            f"{i}. {result}"
            for i, result
            in enumerate(so_results, 1)
        ]))
    else:
        store_results_in_module(exc, so_results)
        try:
            Display().run()
        except Exception as e:
            display_app_error(e)


if __name__ == "__main__":
    main()
