import sys

from rich import print

from pytui.core import get_all_error_results
from pytui.display import Display


def main() -> None:
    """Run the application"""
    no_display = False

    if len(sys.argv) > 1 and sys.argv[1] == '-n':
        no_display = True
        sys.argv.pop(1)

    if len(sys.argv) == 1:
        print("Usage: pytui [-n] <script>")
        sys.exit(1)

    if no_display:
        results = get_all_error_results()
        print(results)

    else:
        Display().run()


if __name__ == "__main__":
    main()
