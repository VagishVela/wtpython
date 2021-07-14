import webbrowser
from typing import Any, List, Union
from urllib.parse import urlencode

from markdownify import MarkdownConverter
from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from textual import events
from textual.app import App
from textual.views import DockView
from textual.widget import Reactive, Widget
from textual.widgets import Footer, Header, ScrollView

from wtpython.backends.stackoverflow import StackOverflowQuestion
from wtpython.settings import APP_NAME

PARSED_TB: dict[str, Any] = {}
SO_RESULTS: list[StackOverflowQuestion] = []


def store_results_in_module(parsed_tb: dict[str, Any], so_results: list[StackOverflowQuestion]) -> None:
    """Unfortunate hack since there is an error with passing values to Display.

    Display inherits App and somwhere in the App.__init__ flow, values are
    overwritten. These global variables are used in lieu of passing to
    Display for now.

    These values are used in `Display.on_startup`
    """
    global SO_RESULTS, PARSED_TB
    SO_RESULTS = so_results
    PARSED_TB = parsed_tb


class PythonCodeConverter(MarkdownConverter):
    """Create a custom MarkdownConverter that adds adds python syntax highlighting."""

    def convert_pre(self, el: Any, text: str, convert_as_inline: bool) -> str:
        """Convert the <pre> tag into a code blocked marked with py"""
        if not text:
            return ''
        return '\n```py\n%s\n```\n' % text


class Sidebar(Widget):
    """Sidebar with list of questions and possible answers"""

    index: Reactive[int] = Reactive(0)

    def set_index(self, index: int) -> None:
        """Set the current question index"""
        self.index = index

    def __init__(self, name: Union[str, None], questions: List[StackOverflowQuestion] = None) -> None:
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
            Align.center(
                self.get_questions(), vertical="top"
            ),
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

        await self.bind("d", "open_browser")
        await self.bind("f", "open_google")

        await self.bind("left", "prev_question")
        await self.bind("right", "next_question")

        # Vim shortcuts...
        await self.bind("k", "prev_question")
        await self.bind("l", "next_question")

    def create_body_text(self) -> RenderableType:
        """Return the text to display in the ScrollView"""
        if self.data['results'] == []:
            return "Could not find any results. Sorry!"

        # For now assume first question... but ideally user should be able to pick
        # the question from the sidebar

        converter = PythonCodeConverter()
        question: StackOverflowQuestion = self.data['results'][self.index]
        text = ""
        text += f'Question #{self.index + 1} - {question.title}\n\n'
        text += f'{converter.convert(question.body)}\n'
        for number, answer in enumerate(question.answers):
            text += f"---\n### Answer {number + 1}\n---\n"
            text += converter.convert(answer.body)
            text += "\n"

        output = Markdown(text, inline_code_lexer="python")
        return output

    async def action_next_question(self) -> None:
        """Go to the next question"""
        if len(self.data["results"]) > self.index + 1:
            self.index += 1
            await self.body.update(self.create_body_text())
            self.body.focus()
            self.sidebar.set_index(self.index)

    async def action_prev_question(self) -> None:
        """Go to the previous question"""
        if self.index != 0:
            self.index -= 1
            await self.body.update(self.create_body_text())
            self.body.focus()
            self.sidebar.set_index(self.index)

    async def action_open_browser(self) -> None:
        """Open the question in the browser"""
        if self.data["results"] != []:
            webbrowser.open(self.data["results"][self.index].link)

    async def action_open_google(self) -> None:
        """Open the browser with google search results"""
        if self.data["error_message"]:
            params = {'q': f"python {self.data['error_message']}"}
            url = 'https://www.google.com/search?' + urlencode(params)
            webbrowser.open(url)

    async def on_startup(self, event: events.Startup) -> None:
        """App layout"""
        self.title = f"{APP_NAME} | {PARSED_TB['error_message']}"
        view = await self.push_view(DockView())
        self.index = 0
        self.data = {'results': SO_RESULTS, **PARSED_TB}
        header = Header()
        footer = Footer()
        self.sidebar = Sidebar("sidebar", self.data["results"])
        self.body = ScrollView(self.create_body_text())

        footer.add_key("q", "Quit")
        footer.add_key("←", "Previous Question")
        footer.add_key("→", "Next Question")
        footer.add_key("s", "Toggle Question List")
        footer.add_key("d", "Open in Browser")
        footer.add_key("f", "Search Google")

        self.body.focus()
        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(self.sidebar, edge="left", size=30)
        await view.dock(self.body, edge="right")
        self.require_layout()
