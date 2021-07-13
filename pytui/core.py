import subprocess  # noqa: S404

import pyperclip

from pytui.arguments import args
from pytui.backends.stackoverflow import StackOverflowFinder
from pytui.parser import parse_traceback


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
