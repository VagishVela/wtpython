import sys

from parsers.python import PythonParser
from backends.stackoverflow import StackOverFlowFinder
from display import Display


def main():
    all_text = sys.stdin.read()

    parser = PythonParser(all_text)
    error_message = parser.parse_error()
    
    backend = StackOverflowFinder()
    search_result = backend.search(error_message)
    
    Display(error_message).start()

if __name__ == "__main__":
    main()