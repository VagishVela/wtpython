from __future__ import annotations

import webbrowser
from typing import Optional

from rich.console import RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.app import App
from textual.views import DockView
from textual.widget import Reactive, Widget
from textual.widgets import Footer, Header, ScrollView

from wtpython.backends import SearchEngine, StackOverflow, Trace
from wtpython.settings import APP_NAME, GH_ISSUES

TRACE: Trace = Trace(Exception())
SO_RESULTS: StackOverflow = StackOverflow('python')
SEARCH: SearchEngine = SearchEngine(Trace(Exception()))


def store_results_in_module(
    trace: Trace, so_results: StackOverflow, search_engine: SearchEngine
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


class Sidebar(Widget):
    """Sidebar widget to display list of questions."""

    index: Reactive[int] = Reactive(0)
    highlighted: Reactive[Optional[int]] = Reactive(None)

    def __init__(
        self,
        name: Optional[str],
        so: StackOverflow,
    ) -> None:
        self.so: StackOverflow = so
        super().__init__(name=name)
        self._text: Optional[Panel] = None

    async def watch_index(self, value: Optional[int]) -> None:
        """If index changes, regenerate the text."""
        self._text = None

    async def watch_highlighted(self, value: Optional[int]) -> None:
        """If highlight key changes we need to regenerate the text."""
        self._text = None
        self.so.highlighted = self.highlighted

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        """Store any key we are moving over."""
        self.highlighted = event.style.meta.get("index")

    async def on_leave(self, event: events.Leave) -> None:
        """Clear any highlight when the mouse leave the widget"""
        self.highlighted = None

    def render(self) -> RenderableType:
        """Render the panel."""
        if self._text is None:
            text = Text(no_wrap=False, overflow="ellipsis")

            for i, item in enumerate(self.so.sidebar()):
                item.apply_meta({"@click": f"app.set_index({i})", "index": i})  # type: ignore
                text.append_text(item)
                text.append_text(Text("\n\n"))

            self._text = Panel(text, title=self.so.sidebar_title)
        return self._text


class TextualDisplay(App):
    """WTPython application."""

    async def on_load(self, event: events.Load) -> None:
        """Key bindings."""
        await self.bind("q", "quit", show=False)
        await self.bind(
            "ctrl+c", "quit", description="Quit", key_display="ctrl+c", show=True
        )

        await self.bind("left", "prev_question", description="Prev", key_display="←")
        await self.bind("right", "next_question", description="Next", key_display="→")

        await self.bind("s", "view.toggle('sidebar')", description="Sidebar")
        await self.bind("t", "show_traceback", description="Toggle Traceback")

        await self.bind("d", "open_browser", description="Open Browser")
        await self.bind("f", "open_search_engine", description="Search Engine")
        await self.bind("i", "report_issue", description="Report Issue")

        # Vim shortcuts...
        await self.bind("k", "prev_question", show=False)
        await self.bind("j", "next_question", show=False)

    def create_body_text(self) -> RenderableType:
        """Generate the text to display in the ScrollView."""
        if self.viewing_traceback:
            return TRACE.rich_traceback

        SO_RESULTS.index = self.index
        output = Markdown(SO_RESULTS.display(), inline_code_lexer="python")
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
        webbrowser.open(SO_RESULTS.active_url)

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
