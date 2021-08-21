from __future__ import annotations

import html
import webbrowser
from typing import Any, Iterable, Optional, Union

from markdownify import MarkdownConverter
from rich.console import RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.app import App
from textual.views import DockView
from textual.widget import Reactive, Widget
from textual.widgets import Footer, Header, ScrollView

from wtpython.search_engine import SearchEngine
from wtpython.settings import APP_NAME, GH_ISSUES, SEARCH_ENGINE
from wtpython.stackoverflow import StackOverflowQuestion
from wtpython.trace import Trace

TRACE: Trace = Trace(Exception())
SO_RESULTS: list[StackOverflowQuestion] = []
SEARCH: SearchEngine = SearchEngine(Exception(), SEARCH_ENGINE)


def store_results_in_module(
    trace: Trace,
    so_results: list[StackOverflowQuestion],
    search_engine: SearchEngine
) -> None:
    """Unfortunate hack since there is an error with passing values to Display.

    Display inherits App and somwhere in the App.__init__ flow, values are
    overwritten. These global variables are used in lieu of passing to
    Display for now.

    These values are used in `Display.on_startup`
    """
    global SO_RESULTS, TRACE, SEARCH
    SO_RESULTS = so_results
    TRACE = trace
    SEARCH = search_engine


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

    def __init__(
        self,
        name: Union[str, None],
        questions: Iterable[StackOverflowQuestion] = (),
    ) -> None:
        self.questions = questions
        super().__init__(name=name)
        self._text: Optional[Text] = None

    async def watch_index(self, value: Optional[int]) -> None:
        """If index changes, regenerate the text."""
        self._text = None

    async def watch_highlighted(self, value: Optional[int]) -> None:
        """If highlight key changes we need to regenerate the text."""
        self._text = None

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        """Store any key we are moving over."""
        self.highlighted = event.style.meta.get("index")

    async def on_leave(self, event: events.Leave) -> None:
        """Clear any highlight when the mouse leave the widget"""
        self.highlighted = None

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
            item_text = Text.assemble(  # type: ignore
                (f"#{i + 1} ", color),
                (f"Score: {question.score}", f"{color} bold"),
                (f"{accepted} - {title}\n\n", f"{color}"),
                meta={"@click": f"app.set_index({i})", "index": i}
            )
            text.append_text(item_text)

        return text

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
        await self.bind("f", "open_search_engine", description="Search Engine")
        await self.bind("i", "report_issue", description="Report Issue")

        # Vim shortcuts...
        await self.bind("k", "prev_question", show=False)
        await self.bind("j", "next_question", show=False)

    def create_body_text(self) -> RenderableType:
        """Generate the text to display in the ScrollView."""
        converter = PythonCodeConverter()

        if self.viewing_traceback:
            return TRACE.rich_traceback
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

    async def action_open_search_engine(self) -> None:
        """Open the browser with search engine results."""
        webbrowser.open(SEARCH.url)

    async def action_show_traceback(self) -> None:
        """Show the traceback."""
        self.viewing_traceback = not self.viewing_traceback
        await self.update_body()

    async def on_mount(self, event: events.Mount) -> None:
        """Main Program"""
        self.title = f"{APP_NAME} | {TRACE.error}"

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
