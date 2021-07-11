import argparse
import sys
from collections import defaultdict

args = defaultdict(lambda: None)


def parse_arguments() -> None:
    """Parse arguments and store them in pytui.arguments.args"""
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("-n", "--no-display",
                        action='store_true',
                        default=False,
                        help="Run without display")
    parser.add_argument("-c", "--copy-error",
                        action='store_true',
                        default=False,
                        help="Copy error to clipboard")
    parser.add_argument("script", help="Python script to run")

    # Keep the remaining arguments in `sys.argv`
    parsed, sys.argv[1:] = parser.parse_known_args()

    global args
    args.update(vars(parsed))
