from parse import findall


def parse_error(txt: str) -> tuple:
    """
    Extract error message and packages involved in stack trace.

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
