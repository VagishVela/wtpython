import webbrowser
from typing import List, Union

import markdownify
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

from pytui.backends.stackoverflow import StackOverflowQuestion
from pytui.core import get_all_error_results


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
                text += f"[yellow]#{i + 1} - "+question.title + "\n\n"
            else:
                text += f"[white]#{i + 1} - "+question.title + "\n\n"

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
        await self.bind("b", "view.toggle('sidebar')")
        await self.bind("up", "prev_question")
        await self.bind("down", "next_question")
        await self.bind("o", "open_browser")

    def create_body_text(self) -> RenderableType:
        """Return the text to display in the ScrollView"""
        if self.data['results'] == []:
            return "Could not find any results. Sorry!"

        # For now assume first question... but ideally user should be able to pick
        # the question from the sidebar

        question: StackOverflowQuestion = self.data['results'][self.index]
        text = ""
        text += f'Question #{self.index + 1} - {question.title}\n\n{markdownify.markdownify(question.body)}\n'
        for number, answer in enumerate(question.answers):
            text += f"---\n### Answer {number + 1}\n---\n"
            text += markdownify.markdownify(answer.body)

            text += "\n"

        output = Markdown(text)
        return output

    async def action_next_question(self) -> None:
        """Go to the next question"""
        if len(self.data["results"]) > self.index + 1:
            self.index += 1
            await self.body.update(self.create_body_text())
            self.sidebar.set_index(self.index)

    async def action_prev_question(self) -> None:
        """Go to the previous question"""
        if self.index != 0:
            self.index -= 1
            await self.body.update(self.create_body_text())
            self.sidebar.set_index(self.index)

    async def action_open_browser(self) -> None:
        """Open the question in the browser"""
        if self.data["results"] != []:
            webbrowser.open(self.data["results"][self.index].link)

    async def on_startup(self, event: events.Startup) -> None:
        """App layout"""
        view = await self.push_view(DockView())
        self.index = 0
        self.data = get_all_error_results()
        header = Header()
        footer = Footer()
        self.sidebar = Sidebar("Sidebar", self.data["results"])
        self.body = ScrollView(self.create_body_text())

        footer.add_key("b", "Toggle sidebar")
        footer.add_key("q", "Quit")
        footer.add_key("o", "Open question in browser")
        footer.add_key("^", "Previous question")
        footer.add_key("v", "Next question")

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(self.sidebar, edge="left", size=30)
        await view.dock(self.body, edge="right")
        self.require_layout()
