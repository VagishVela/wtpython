import subprocess  # noqa: S404
import sys

from parse import findall

from pytui.display.display import Display


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
        error_message = f"[red bold]Error Message:[/] {error_msg}"
        error_message += f"[blue bold]Packages:[/] {', '.join(packages)}"

    display = Display(title="Simple App")
    display.run()


if __name__ == "__main__":
    main()
