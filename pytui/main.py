import subprocess  # noqa: S404
import sys

from backends.stackoverflow import StackOverflowFinder
from parse import findall
from rich import print


def parse_err(txt: str) -> tuple:
    """Extract error message and packages involved in stack trace.

    The specific error message is assumed to be the last line that is not indented.
    """
    error_msg = ''
    for line in txt.splitlines():
        if line == line.strip():
            error_msg = line.strip()

    files = [
        line['file']
        for line
        in findall('File "{file}", line {line_no}, in {method}', txt)
    ]

    packages = set()
    key = 'site-packages'
    for file in files:
        if key not in file:
            continue
        path_elements = file.split('/')
        packages.add(path_elements[path_elements.index(key) + 1])

    return error_msg, packages


def main() -> None:
    """Run the application"""
    args = sys.argv
    args[0] = 'python'  # Replace pytui with 'python' to act as a runner
    result = subprocess.run(args, stderr=subprocess.PIPE, shell=False)  # noqa: S603

    if result.stderr:
        error_msg, packages = parse_err(result.stderr.decode('utf-8'))
        print(f"[red bold]Error Message:[/] {error_msg}")
        print(f"[blue bold]Packages:[/] {', '.join(packages)}")
        stack_overflow = StackOverflowFinder()
        error_answers = stack_overflow.search(error_msg, 10)  # noqa: F841
        # Do stuff with error_answers and show to user in TUI


if __name__ == "__main__":
    main()
