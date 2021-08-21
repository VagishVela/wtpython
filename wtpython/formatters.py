from typing import Any, Optional

from markdownify import MarkdownConverter


def rich_link(url: str, text: Optional[str] = None) -> str:
    """
    Create a link to a URL.

    :param url: The URL to link to.
    :param text: The text to display for the link. Defaults to the URL.
    :return: The HTML link.
    """
    if text is None:
        text = url
    return f"[link={url}]{text}[/link]"


class PythonCodeConverter(MarkdownConverter):
    """Custom MarkdownConverter to add python syntax highlighting."""

    def convert_pre(self, el: Any, text: str, convert_as_inline: bool) -> str:
        """Add python syntax to all <pre> elements."""
        if not text:
            return ""
        return "\n```py\n%s\n```\n" % text
