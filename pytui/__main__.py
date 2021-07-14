import pyperclip
from rich import print

from pytui.backends.stackoverflow import StackOverflowFinder
from pytui.core import parse_arguments, parse_traceback, run_and_get_stderr
from pytui.display import Display, store_results_in_module
from pytui.settings import MAX_SO_RESULTS


def main() -> None:
    """Run the application"""
    flags, args = parse_arguments()
    tb = run_and_get_stderr(args)
    parsed_tb = parse_traceback(tb)

    so = StackOverflowFinder()
    so_results = so.search(parsed_tb["error_message"], MAX_SO_RESULTS)

    store_results_in_module(parsed_tb, so_results)

    if flags["copy_error"]:
        pyperclip.copy(parsed_tb["error_message"])

    if flags['no_display']:
        print(parsed_tb)
        print(so_results)
    else:
        Display().run()


if __name__ == "__main__":
    main()
