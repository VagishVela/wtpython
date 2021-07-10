import sys

from backends.stackoverflow import StackOverflowFinder
from display.display import Display
from parsers.python import PythonParser


def main() -> None:
    """Run the application"""
    all_text = sys.stdin.read()

    parser = PythonParser(all_text)
    error_message = parser.parse_error()
    backend = StackOverflowFinder()
    search_results = backend.search(error_message)
    Display(error_message, search_results).start()


if __name__ == "__main__":
    main()
