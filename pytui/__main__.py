import sys

from pytui.display import Display


def main() -> None:
    """Run the application"""
    if len(sys.argv) == 1:
        print("Usage: pytui <script>")
        sys.exit(1)

    Display().run()


if __name__ == "__main__":
    main()
