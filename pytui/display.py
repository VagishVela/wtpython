import markdownify
from rich.console import RenderableType
from rich.markdown import Markdown
from textual import events
from textual.app import App
from textual.views import DockView
from textual.widgets import Footer, Header, Placeholder, ScrollView

from pytui.backends.stackoverflow import StackOverflowQuestion
from pytui.core import get_all_error_results


class Display(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        """Navigation setup for display"""
        await self.bind("q,ctrl+c", "quit")
        await self.bind("b", "view.toggle('sidebar')")
        await self.bind("up", "prev_question")
        await self.bind("down", "next_question")

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

    async def action_prev_question(self) -> None:
        """Go to the previous question"""
        if self.index != 0:
            self.index -= 1
            await self.body.update(self.create_body_text())

    async def on_startup(self, event: events.Startup) -> None:
        """App layout"""
        view = await self.push_view(DockView())
        self.index = 0
        self.data = get_all_error_results()
        header = Header()
        footer = Footer()
        self.sidebar = Placeholder(name="sidebar")
        self.body = ScrollView(self.create_body_text())

        footer.add_key("b", "Toggle sidebar")
        footer.add_key("q", "Quit")

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(self.sidebar, edge="left", size=30)
        await view.dock(self.body, edge="right")
        self.require_layout()
