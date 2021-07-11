from textual import events
from textual.app import App
from textual.view import DockView
from textual.widgets import Footer, Header, Placeholder, ScrollView

from pytui.parsers.parse_errors import run_and_get_errors


class Display(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        """Navigation setup for display"""
        await self.bind("q,ctrl+c", "quit")
        await self.bind("b", "view.toggle('sidebar')")

    async def on_startup(self, event: events.Startup) -> None:
        """App layout"""
        self.error, self.packages = run_and_get_errors()
        view = await self.push_view(DockView())
        header = Header(self.title)
        footer = Footer()
        sidebar = Placeholder(name="sidebar")

        body = ScrollView(self.error)

        footer.add_key("b", "Toggle sidebar")
        footer.add_key("q", "Quit")

        await view.dock(header, edge="top")
        await view.dock(footer, edge="bottom")
        await view.dock(sidebar, edge="left", size=30)
        await view.dock(body, edge="right")
        self.require_layout()
