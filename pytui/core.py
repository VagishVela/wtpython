import argparse
import subprocess  # noqa: S404
import sys
from collections import defaultdict
from typing import Any

import pyperclip
from parse import findall

from pytui.backends.stackoverflow import StackOverflowFinder

args = defaultdict(lambda: None)


def run_and_get_stderr() -> str:
    """Run the python script and return the stderr output"""
    # TODO: Perhaps add a way to also pass in extra arguments
    run_args = ["python", args['script']]
    process = subprocess.run(run_args, stderr=subprocess.PIPE, shell=False)  # noqa: S603

    if not process.stderr:
        return None

    return process.stderr.decode('utf-8')


def get_all_error_results(max_results: int = 10) -> dict:
    """
    This is the core function that runs the script and returns error results

    The script name is read from `sys.argv`, and the stderr output of the
    program is parsed for the error. This error is then passed to the
    StackOverflow backend and all the results are returned.
    """
    all_text = run_and_get_stderr()
    parsed = parse_traceback(all_text)

    # Copy the error to the clipboard if asked
    if args["copy_error"]:
        pyperclip.copy(parsed["error_message"])

    stack_overflow = StackOverflowFinder()
    error_answers = stack_overflow.search(parsed["error_message"], max_results)

    return {"results": error_answers, **parsed}


def _error_message(txt: str) -> str:
    """The specific error message is assumed to be the last line that is not indented."""
    error_message = ''
    for line in txt.splitlines():
        if line == line.strip():
            error_message = line.strip()
    return error_message


def _error_files(txt: str) -> list[dict[str, str]]:
    """Extract files named in traceback."""
    return [
        line.named
        for line
        in findall('File "{file}", line {line}, in {method}\n', txt)
    ]


def _extract_packages(files: list[dict[str, str]]) -> set[str]:
    """Extract file info from each file reference."""
    packages = set()
    key = 'site-packages'
    for file_info in files:
        file = file_info['file']
        if key not in file:
            continue
        path_elements = file.split('/')
        packages.add(path_elements[path_elements.index(key) + 1])
    return packages


def parse_traceback(txt: str) -> dict[str, Any]:
    """Extract error message and packages involved in traceback."""
    error_message = _error_message(txt)
    files = _error_files(txt)
    packages = _extract_packages(files)

    return {
        'error_message': error_message,
        'files': files,
        'packages': packages,
        'traceback': txt,
    }


def parse_arguments() -> None:
    """Parse arguments and store them in pytui.arguments.args"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-display",
                        action='store_true',
                        default=False,
                        help="Run without display")
    parser.add_argument("-c", "--copy-error",
                        action='store_true',
                        default=False,
                        help="Copy error to clipboard")
    parser.add_argument("script", help="Python script to run")

    # Keep the remaining arguments in `sys.argv`
    parsed, sys.argv[1:] = parser.parse_known_args()

    global args
    args.update(vars(parsed))
