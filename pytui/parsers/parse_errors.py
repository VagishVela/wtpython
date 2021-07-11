import subprocess  # noqa: S404
import sys
from typing import Tuple

from parse import findall


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


def run_and_get_errors() -> Tuple[str, str]:
    """Run the python script and find errors."""
    args = sys.argv
    args[0] = 'python'  # Replace pytui with 'python' to act as a runner
    result = subprocess.run(args, stderr=subprocess.PIPE, shell=False)  # noqa: S603

    if result.stderr:
        error_msg, packages = parse_err(result.stderr.decode('utf-8'))
        return error_msg, packages
