from typing import Any

from parse import findall


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
