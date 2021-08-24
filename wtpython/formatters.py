from typing import Any, Optional

from markdownify import MarkdownConverter


def rich_link(url: str, text: Optional[str] = None) -> str:
    """
    Create a link to a URL.

    Args:
        url: The URL to link to.
        text: The text to display for the link. Defaults to the URL.

    Returns:
        The URL formatted with Rich's link syntax.
    """
    if text is None:
        text = url
    return f"[link={url}]{text}[/link]"


class PythonCodeConverter(MarkdownConverter):
    """Custom MarkdownConverter to add python syntax highlighting."""

    def convert_pre(self, el: Any, text: str, convert_as_inline: bool) -> str:
        """Add python syntax to all <pre> elements.

        Args:
            el: The element to convert.
            text: The text to convert.
            convert_as_inline: Whether to convert the element as inline.

        Returns:
            text of pre element primed for python syntax highlighting.
        """
        if not text:
            return ""
        return "\n```py\n%s\n```\n" % text
