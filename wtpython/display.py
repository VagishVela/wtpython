import traceback
import webbrowser
from typing import Any, List, Union
from urllib.parse import urlencode

from markdownify import MarkdownConverter
from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.traceback import Traceback
from textual import events
from textual.app import App
from textual.views import DockView
from textual.widget import Reactive, Widget
from textual.widgets import Footer, Header, ScrollView

from wtpython.backends.stackoverflow import StackOverflowQuestion
from wtpython.settings import APP_NAME, GH_ISSUES

RAISED_EXC: Exception = None
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
    """Create a custom MarkdownConverter that adds adds python syntax highlighting."""

    def convert_pre(self, el: Any, text: str, convert_as_inline: bool) -> str:
        """Convert the <pre> tag into a code blocked marked with py"""
        if not text:
            return ""
        return "\n```py\n%s\n```\n" % text


class Sidebar(Widget):
    """Sidebar with list of questions and possible answers"""

    index: Reactive[int] = Reactive(0)

    def set_index(self, index: int) -> None:
        """Set the current question index"""
        self.index = index

    def __init__(
        self, name: Union[str, None], questions: List[StackOverflowQuestion] = None
    ) -> None:
        if questions is not None:
            self.questions = questions
        super().__init__(name=name)

    def get_questions(self) -> str:
        """Put questions into legible format"""
        text = ""
        for i, question in enumerate(self.questions):
            if i == self.index:
                text += f"[yellow]#{i + 1} - {question.title}[/yellow]\n\n"
            else:
                text += f"[white]#{i + 1} - {question.title}[/white]\n\n"

        return text

    def render(self) -> RenderableType:
        """Render the panel"""
        return Panel(
            Align.center(self.get_questions(), vertical="top"),
            title="Questions",
            border_style="blue",
            box=box.ROUNDED,
        )


class Display(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        """Navigation setup for display"""
        await self.bind("q,ctrl+c", "quit")
        await self.bind("s", "view.toggle('sidebar')")
        await self.bind("t", "show_traceback")

        await self.bind("d", "open_browser")
        await self.bind("f", "open_google")
        await self.bind("i", "report_issue")

        await self.bind("left", "prev_question")
        await self.bind("right", "next_question")

        # Vim shortcuts...
        await self.bind("k", "prev_question")
        await self.bind("j", "next_question")

    def create_body_text(self) -> RenderableType:
        """Return the text to display in the ScrollView"""
        converter = PythonCodeConverter()

        if self.viewing_traceback:
            return Traceback.from_exception(
                type(RAISED_EXC),
                RAISED_EXC,
                RAISED_EXC.__traceback__,
            )
        if SO_RESULTS == []:
            return "Could not find any results. Sorry!"

        # For now assume first question... but ideally user should be able to pick
        # the question from the sidebar

        question: StackOverflowQuestion = SO_RESULTS[self.index]
        text = ""
        text += f"# {question.title} | {question.score} vote{'s' if question.score != 1 else ''}\n"
        text += f"{converter.convert(question.body)}\n"
        for number, answer in enumerate(question.answers):
            text += (
                f"---\n### Answer #{number + 1} | "
                f"{answer.score} vote{'s' if answer.score != 1 else ''}"
                f"{' | [Accepted]' if answer.is_accepted else ''}"
                f"\n---\n "
            )
            text += converter.convert(answer.body)
            text += "\n"

        output = Markdown(text, inline_code_lexer="python")
        return output

    async def update_body(self) -> None:
        """Update the body"""
        await self.body.update(self.create_body_text())
        self.body.y = 0
        self.body.target_y = 0

    async def action_next_question(self) -> None:
        """Go to the next question"""
        if len(SO_RESULTS) > self.index + 1:
            self.viewing_traceback = False
            self.index += 1
            await self.update_body()
            self.sidebar.set_index(self.index)

    async def action_prev_question(self) -> None:
        """Go to the previous question"""
        if self.index != 0:
            self.viewing_traceback = False
            self.index -= 1
            await self.update_body()
            self.sidebar.set_index(self.index)

    async def action_open_browser(self) -> None:
        """Open the question in the browser"""
        if SO_RESULTS != []:
            webbrowser.open(SO_RESULTS[self.index].link)

    async def action_report_issue(self) -> None:
        """Take user to submit new issue on Github."""
        webbrowser.open(GH_ISSUES)

    async def action_open_google(self) -> None:
        """Open the browser with google search results"""
        exc_msg = "".join(
            traceback.format_exception_only(type(RAISED_EXC), RAISED_EXC)
        ).strip()
        params = {"q": f"python {exc_msg}"}
        url = "https://www.google.com/search?" + urlencode(params)
        webbrowser.open(url)

    async def action_show_traceback(self) -> None:
        """Show the traceback"""
        self.viewing_traceback = not self.viewing_traceback
        await self.update_body()

    async def on_startup(self, event: events.Startup) -> None:
        """App layout"""
        exc_msg = "".join(
            traceback.format_exception_only(type(RAISED_EXC), RAISED_EXC)
        ).strip()
        self.title = f"{APP_NAME} | {exc_msg}"
        view = await self.push_view(DockView())
        self.index = 0
        self.viewing_traceback = False
        header = Header()
        footer = Footer()
        self.sidebar = Sidebar("sidebar", SO_RESULTS)
        self.body = ScrollView(self.create_body_text())

        footer.add_key("q", "Quit")
        footer.add_key("←", "Previous Question")
        footer.add_key("→", "Next Question")
        footer.add_key("t", "Toggle Traceback")
        footer.add_key("s", "Toggle Question List")
        footer.add_key("d", "Open in Browser")
        footer.add_key("f", "Search Google")
        footer.add_key("i", "Report Issue")

        await self.set_focus(self.body.page)

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(self.sidebar, edge="left", size=30)
        await view.dock(self.body, edge="right")
        self.require_layout()
