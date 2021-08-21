from __future__ import annotations

import html
import traceback
import webbrowser
from copy import copy
from typing import Any, Iterable, Optional, Union
from urllib.parse import urlencode

from markdownify import MarkdownConverter
from rich.console import Console, RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.traceback import Traceback
from textual import events
from textual.app import App
from textual.geometry import Size
from textual.views import DockView
from textual.widget import Reactive, Widget
from textual.widgets import Footer, Header, ScrollView

from wtpython.settings import APP_NAME, GH_ISSUES
from wtpython.stackoverflow import StackOverflowQuestion

RAISED_EXC: Exception = Exception()
SO_RESULTS: list[StackOverflowQuestion] = []


def store_results_in_module(
    raised_exc: Exception, so_results: list[StackOverflowQuestion]
) -> None:
    """Unfortunate hack since there is an error with passing values to Display.

    Display inherits App and somwhere in the App.__init__ flow, values are
    overwritten. These global variables are used in lieu of passing to
    Display for now.

    These values are used in `Display.on_startup`
    """
    global SO_RESULTS, RAISED_EXC
    SO_RESULTS = so_results
    RAISED_EXC = raised_exc


class PythonCodeConverter(MarkdownConverter):
    """Custom MarkdownConverter to add python syntax highlighting."""

    def convert_pre(self, el: Any, text: str, convert_as_inline: bool) -> str:
        """Add python syntax to all <pre> elements."""
        if not text:
            return ""
        return "\n```py\n%s\n```\n" % text


def check_overflow(contents: list[Text], console: Console, size: Size) -> bool:
    """Simulate end result, and check if the controls are visible"""
    page = Text(end="")
    for i in contents:
        page.append_text(i)
    page.append_text(
        Text.assemble(  # type: ignore
            "<- Prev"
        )
    )

    page.append_text(
        Text.assemble(
            " Page 0/0 "
        )
    )

    page.append_text(
        Text.assemble(  # type: ignore
            "Next ->"
        )
    )

    panel = Panel(page, title="Questions")

    output = panel.__rich_console__(console, console.options.update_dimensions(size[0], size[1]))
    output = list(output)
    output = [i.text for i in output]  # type: ignore

    output = "".join(output)  # type: ignore

    return "<- Prev Page 0/0 Next ->" not in output


def get_height(text: Text, console: Console, size: Size) -> int:
    """Get the height of a rendered text panel"""
    panel = Panel(text)

    output = panel.__rich_console__(console, console.options.update_dimensions(size[0], size[1] + 50))
    output = list(output)
    output = [i.text for i in output]  # type: ignore
    output = "".join(output).split("\n")  # type: ignore

    output.pop(-1)
    output.pop(-1)
    output.pop(0)

    output.reverse()
    blank_line = output[0]
    output2 = copy(output)

    for i in output:
        if i == blank_line:
            output2.pop(0)
        else:
            break

    output2.reverse()

    return len(output2)


class Sidebar(Widget):
    """Sidebar widget to display list of questions."""

    index: Reactive[int] = Reactive(0)
    highlighted: Reactive[Optional[int]] = Reactive(None)
    page: Reactive[int] = Reactive(0)
    pages: Reactive[list[Text]] = Reactive([])

    def __init__(
        self,
        name: Union[str, None],
        questions: Iterable[StackOverflowQuestion] = (),
    ) -> None:
        super().__init__(name=name)
        self._text: Optional[Text] = None
        self.questions = questions
        self.pages: list[Text] = []

    def update_pages(self):  # noqa: ANN201
        """Update the pages, and the pages_index"""
        self.pages = []
        current_page = Text(end="")
        current_page_container = []
        current_page_contents = []
        pages_index = {}
        pages = []
        on_next = None

        for i, question in enumerate(self.questions):
            if on_next is not None:
                current_page_contents.append(on_next[0])
                current_page_container.append(on_next[1])
                on_next = None

            title = html.unescape(question.title)
            color = 'yellow' if i == self.index else ('grey' if self.highlighted == i else 'white')
            accepted = '✔️ ' if any(ans.is_accepted for ans in question.answers) else ''
            item_text = Text.assemble(  # type: ignore
                (f"#{i + 1} ", color),
                (f"Score: {question.score}", f"{color} bold"),
                (f"{accepted} - {title}\n\n", f"{color}"),
                meta={"@click": f"app.set_index({i})", "index": i}
            )
            current_page_contents.append(item_text)
            current_page.append_text(item_text)
            current_page_container.append(i)

            if len(current_page_contents) != 1 and check_overflow(current_page_contents, self.app.console, self.size):
                page = Text(end="")
                on_next = (current_page_contents.pop(), current_page_container.pop())
                for i in current_page_contents:
                    page.append_text(i)
                for i in current_page_container:
                    pages_index[i] = len(pages)
                pages.append(page)
                current_page_contents = []
                current_page_container = []
                current_page = Text(end="")

        if on_next is not None:
            current_page_contents.append(on_next[0])
            current_page_container.append(on_next[1])
        if len(current_page_contents) != 0:
            page = Text(end="")
            for i in current_page_contents:
                page.append_text(i)
            for i in current_page_container:
                pages_index[i] = len(pages)
            pages.append(page)

        self.pages_index = pages_index
        self.pages = pages

    async def watch_index(self, value: Optional[int]) -> None:
        """If index changes, regenerate the text."""
        self._text = None
        self.page = self.pages_index[self.index]

    async def watch_page(self, value: Optional[int]) -> None:
        """If page changes, regenerate the text."""
        self._text = None

    async def watch_highlighted(self, value: Optional[int]) -> None:
        """If highlight key changes we need to regenerate the text."""
        self._text = None

    async def on_resize(self, event: events.Resize) -> None:
        """Regenerate text on resize"""
        self._text = None

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        """Store any key we are moving over."""
        self.highlighted = event.style.meta.get("index")

    async def on_leave(self, event: events.Leave) -> None:
        """Clear any highlight when the mouse leave the widget"""
        self.highlighted = None

    def get_questions(self) -> Text:
        """Format question list."""
        self.update_pages()

        page = self.pages[self.page]

        if len(self.pages) > 1:
            height = get_height(page, self.app.console, self.size)

            extra_lines = self.size.height - height - 4

            page.append_text(
                Text(
                    "\n" * extra_lines
                )
            )
            width = self.size.width - 2

            page.append_text(
                Text(
                    " " * ((width - len(f"<- Prev Page {self.page}/{len(self.pages)} Next ->")) // 2)
                )
            )

            page.append_text(
                Text.assemble(  # type: ignore
                    (
                        "<- Prev",
                        ("grey" if self.highlighted == -1 else "white") \
                        if self.page > 0 else "#4f4f4f"
                    ),
                    meta={"@click": ("app.prev_page" if self.page > 0 else "app.bell"), "index": -1}
                )
            )

            page.append_text(
                Text.assemble(
                    (f" Page {self.page + 1}/{len(self.pages)} ", "yellow")
                )
            )

            page.append_text(
                Text.assemble(  # type: ignore
                    (
                        "Next ->",
                        ("grey" if self.highlighted == -2 else "white") \
                        if self.page > 0 else "#4f4f4f"
                    ),
                    meta={"@click": ("app.next_page" if self.page + 1 < len(self.pages) else "app.bell"), "index": -2}
                )
            )

        return page

    def render(self) -> RenderableType:
        """Render the panel."""
        if self._text is None:
            self._text = Panel(  # type: ignore
                self.get_questions(),
                title="Questions",
            )
        return self._text  # type: ignore


class Display(App):
    """WTPython application."""

    async def on_load(self, event: events.Load) -> None:
        """Key bindings."""
        await self.bind("q", "quit", show=False)
        await self.bind("ctrl+c", "quit", description="Quit", key_display="ctrl+c", show=True)

        await self.bind("left", "prev_question", description="Prev Q", key_display="←")
        await self.bind("right", "next_question", description="Next Q", key_display="→")

        await self.bind("s", "view.toggle('sidebar')", description="Show Questions")
        await self.bind("t", "show_traceback", description="Toggle Traceback")

        await self.bind("d", "open_browser", description="Open Browser")
        await self.bind("f", "open_google", description="Google")
        await self.bind("i", "report_issue", description="Report Issue")

        # Vim shortcuts...
        await self.bind("k", "prev_question", show=False)
        await self.bind("j", "next_question", show=False)

    def create_body_text(self) -> RenderableType:
        """Generate the text to display in the ScrollView."""
        converter = PythonCodeConverter()

        if self.viewing_traceback:
            return Traceback.from_exception(
                type(RAISED_EXC),
                RAISED_EXC,
                RAISED_EXC.__traceback__,
            )
        if SO_RESULTS == []:
            return "Could not find any results. Sorry!"

        question: StackOverflowQuestion = SO_RESULTS[self.index]
        text = ""
        text += f"# {question.title} | Score: {question.score}\n"
        text += f"{converter.convert(question.body)}\n"
        for i, answer in enumerate(question.answers, 1):
            text += (
                f"---\n### Answer #{i} | Score: {answer.score}"
                f"{' ✔️' if answer.is_accepted else ''}"
                "\n---\n "
            )
            text += converter.convert(answer.body)
            text += "\n"

        output = Markdown(text, inline_code_lexer="python")
        return output

    async def update_body(self) -> None:
        """Update the ScrollView body."""
        await self.body.update(self.create_body_text())
        self.body.y = 0
        self.body.target_y = 0

    async def action_set_index(self, index: int) -> None:
        """Set question index"""
        self.sidebar.index = index
        self.index = index
        await self.update_body()

    async def action_next_page(self) -> None:
        """Set page"""
        self.sidebar.page += 1

    async def action_prev_page(self) -> None:
        """Set page"""
        self.sidebar.page -= 1

    async def action_next_question(self) -> None:
        """Go to the next question."""
        if self.index + 1 < len(SO_RESULTS):
            self.viewing_traceback: bool = False
            self.index += 1
            await self.update_body()
            self.sidebar.index = self.index

    async def action_prev_question(self) -> None:
        """Go to the previous question."""
        if self.index:
            self.viewing_traceback = False
            self.index -= 1
            await self.update_body()
            self.sidebar.index = self.index

    async def action_open_browser(self) -> None:
        """Open the question in the browser."""
        if SO_RESULTS != []:
            webbrowser.open(SO_RESULTS[self.index].link)

    async def action_report_issue(self) -> None:
        """Take user to submit new issue on Github."""
        webbrowser.open(GH_ISSUES)

    async def action_open_google(self) -> None:
        """Open the browser with google search results."""
        exc_msg = "".join(
            traceback.format_exception_only(type(RAISED_EXC), RAISED_EXC)
        ).strip()
        params = {"q": f"python {exc_msg}"}
        url = "https://www.google.com/search?" + urlencode(params)
        webbrowser.open(url)

    async def action_show_traceback(self) -> None:
        """Show the traceback."""
        self.viewing_traceback = not self.viewing_traceback
        await self.update_body()

    async def on_mount(self, event: events.Mount) -> None:
        """Main Program"""
        exc_msg = "".join(
            traceback.format_exception_only(type(RAISED_EXC), RAISED_EXC)
        ).strip()
        self.title = f"{APP_NAME} | {exc_msg}"

        view = await self.push_view(DockView())
        self.index = 0
        self.viewing_traceback = False
        header = Header()
        footer = Footer()
        self.sidebar: Sidebar = Sidebar("sidebar", SO_RESULTS)
        self.body: ScrollView = ScrollView(self.create_body_text())

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(self.sidebar, edge="left", size=35)
        await view.dock(self.body, edge="right")


if __name__ == "__main__":
    from wtpython.stackoverflow import StackOverflowFinder
    results = StackOverflowFinder().search("ZeroDivisionError: division by zero")
    try:
        1 / 0
    except ZeroDivisionError as e:
        store_results_in_module(e, results)

    Display().run()
