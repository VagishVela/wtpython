import html2text
from rich.console import RenderableType
from rich.markdown import Markdown
from textual import events
from textual.app import App
from textual.views import DockView
from textual.widgets import Footer, Header, Placeholder, ScrollView

from pytui.core import get_all_error_results
from pytui.settings import APP_NAME


class Display(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        """Navigation setup for display"""
        await self.bind("q,ctrl+c", "quit")
        await self.bind("b", "view.toggle('sidebar')")

    def create_body_text(self) -> RenderableType:
        """Return the text to display in the ScrollView"""
        if self.data['results'] == []:
            return "Could not find any results. Sorry!"

        # For now assume first question... but ideally user should be able to pick
        # the question from the sidebar
        question = self.data['results'][0]

        text = ""
        for index, answer in enumerate(question.answers):
            text += f"---\n### Answer {index}\n---\n"
            text += html2text.html2text(answer.body)
            text += "\n"

        output = Markdown(text)
        return output

    async def on_startup(self, event: events.Startup) -> None:
        """App layout"""
        view = await self.push_view(DockView())

        self.data = get_all_error_results()
        self.title = f"{APP_NAME}: {self.data['error_message']}"

        header = Header()
        footer = Footer()
        sidebar = Placeholder(name="sidebar")

        body = ScrollView(self.create_body_text())

        footer.add_key("b", "Toggle sidebar")
        footer.add_key("q", "Quit")

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(sidebar, edge="left", size=30)
        await view.dock(body, edge="right")
        self.require_layout()
