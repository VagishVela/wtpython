from rich import print

from pytui.core import args, get_all_error_results, parse_arguments
from pytui.display import Display


def main() -> None:
    """Run the application"""
    parse_arguments()

    if args['no_display']:
        print(get_all_error_results())

    else:
        Display().run()


if __name__ == "__main__":
    main()
