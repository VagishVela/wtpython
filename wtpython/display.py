from __future__ import annotations

import html
import traceback
import webbrowser
from typing import Any, Iterable, Optional, Union
from urllib.parse import urlencode

from markdownify import MarkdownConverter
from rich import box
import rich
from rich.align import Align
from rich.console import RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.traceback import Traceback
from rich.text import Text
from textual import events
from textual.app import App
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


class Sidebar(Widget):
    """Sidebar widget to display list of questions."""

    index: Reactive[int] = Reactive(0)
    highlighted: Reactive[Optional[int]] = Reactive(None)

    async def watch_highlighted(self, value) -> None:
        """If highlight key changes we need to regenerate the text."""
        self.text = None

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        """Store any key we are moving over."""
        self.highlighted = event.style.meta.get("index")

    async def on_leave(self, event: events.Leave) -> None:
        """Clear any highlight when the mouse leave the widget"""
        self.highlighted = None

    def __init__(
        self,
        name: Union[str, None],
        questions: Iterable[StackOverflowQuestion] = (),
    ) -> None:
        self.questions = questions
        super().__init__(name=name)
        self.text: Text | None = None

    def get_questions(self) -> Text:
        """Format question list."""
        text = Text(
            no_wrap=False,
            overflow='ellipsis',
        )
        for i, question in enumerate(self.questions):
            title = html.unescape(question.title)
            color = 'yellow' if i == self.index else ('grey' if self.highlighted == i else 'white')
            accepted = '✔️ ' if any(ans.is_accepted for ans in question.answers) else ''
            item_text = Text.assemble(
                (f"#{i + 1} ", color),
                (f"Score: {question.score}", f"{color} bold"),
                (f"{accepted} - {title}\n\n", f"{color}"),
                meta={"@click": f"app.set_index({i})", "index": i}
            )
            text.append_text(item_text)

        return text

    def render(self) -> RenderableType:
        """Render the panel."""
        if self.text is None:
            self.text = Panel(
                self.get_questions(),
                title="Questions",
            )
        return self.text


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

    async def action_set_index(self, index: int):
        self.sidebar.index = index
        self.index = index
        await self.update_body()

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
