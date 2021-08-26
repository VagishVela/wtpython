from __future__ import annotations

import webbrowser
from typing import Optional

from rich.console import Console, RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.app import App
from textual.geometry import Size
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
    page: Reactive[int] = Reactive(0)
    highlighted: Reactive[Optional[int]] = Reactive(None)

    def __init__(
        self,
        name: Optional[str],
        so: StackOverflow,
    ) -> None:
        self.so: StackOverflow = so
        super().__init__(name=name)
        self._text: Optional[Panel] = None
        self.pages: Optional[list[Text]] = None
        self.pages_index: dict[int, int] = {}

    @staticmethod
    def check_overflow(contents: list[Text], console: Console, size: Size) -> bool:
        """Simulate end result, and check if the controls are visible"""
        page = Text(end="")
        for i in contents:
            page.append_text(i)
            page.append_text(Text("\n\n"))
        page.append_text(
            Text.assemble(
                "\n<- Prev"
            )
        )

        page.append_text(
            Text.assemble(
                " Page 0/0 "
            )
        )

        page.append_text(
            Text.assemble(
                "Next ->"
            )
        )

        panel = Panel(page, title="Questions")

        output = panel.__rich_console__(console, console.options.update_dimensions(size[0], size[1]))
        output = list(output)
        output = [i.text for i in output]

        output = "".join(output)

        return "<- Prev Page 0/0 Next ->" not in output

    @staticmethod
    def get_height(text: Text, console: Console, size: Size) -> int:
        """Get the height of a rendered text panel"""
        panel = Panel(text)

        output = panel.__rich_console__(console, console.options.update_dimensions(size[0], size[1] + 50))
        output = list(output)
        output = [i.text for i in output]
        output = "".join(output).split("\n")

        output.pop(-1)
        output.pop(-1)
        output.pop(0)

        output.reverse()
        blank_line = output[0]
        output2 = output.copy()

        for i in output:
            if i == blank_line:
                output2.pop(0)
            else:
                break

        output2.reverse()

        return len(output2)

    async def watch_page(self, value: Optional[int]) -> None:
        """If page changes, regenerate the text."""
        self._text = None

    async def watch_index(self, value: Optional[int]) -> None:
        """If index changes, regenerate the text."""
        self._text = None
        self.so.index = self.index
        self.page = self.pages_index[self.index]

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

    async def on_resize(self, event: events.Resize) -> None:
        """Update the pages on resize"""
        self._text = None

    def update_pages(self) -> None:
        """Update the pages and the pages index"""
        current_page = Text(end="")
        current_page_container: list[int] = []
        current_page_contents: list[Text] = []
        pages_index: dict[int, int] = {}
        pages: list[Text] = []
        on_next = None
        length = 0

        for i, item_text in enumerate(self.so.sidebar()):
            if on_next is not None:
                current_page_contents.append(on_next[0])
                current_page_container.append(on_next[1])
                on_next = None

            current_page_contents.append(item_text)
            current_page.append_text(item_text)
            current_page.append_text(Text("\n\n"))
            current_page_container.append(i)

            overflow = len(current_page_contents) != 1 and \
                self.check_overflow(current_page_contents, self.app.console, self.size)

            if overflow:
                page = Text(end="")
                on_next = (current_page_contents.pop(), current_page_container.pop())

                for index, i in enumerate(current_page_contents):
                    index += length
                    i.apply_meta({"@click": f"app.set_index({index})", "index": index})  # type: ignore
                    page.append_text(i)
                    page.append_text(Text("\n\n"))
                length += len(current_page_contents)
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
            for index, i in enumerate(current_page_contents):
                index += length
                i.apply_meta({"@click": f"app.set_index({index})", "index": index})  # type: ignore
                page.append_text(i)
                page.append_text(Text("\n\n"))
            for i in current_page_container:
                pages_index[i] = len(pages)
            pages.append(page)

        self.pages_index = pages_index
        self.pages = pages

    def render(self) -> RenderableType:
        """Render the panel."""
        if self._text is None:
            self.update_pages()
            try:
                page = self.pages[self.page]  # type: ignore
            except IndexError:
                page = self.pages[len(self.pages) - 1]  # type: ignore

            if len(self.pages) > 1:  # type: ignore
                height = self.get_height(page, self.app.console, self.size)

                extra_lines = self.size.height - height - 4

                page.append_text(
                    Text(
                        "\n" * extra_lines
                    )
                )
                width = self.size.width - 2

                page.append_text(
                    Text(
                        " " * (
                            (width - len(f"<- Prev Page {self.page}/{len(self.pages)} Next ->")) // 2  # type: ignore
                        )
                    )
                )

                page.append_text(
                    Text.assemble(
                        (
                            "<- Prev",
                            ("grey" if self.highlighted == -1 else "white") if self.page > 0 else "#4f4f4f"
                        ),
                        meta={"@click": ("app.prev_page" if self.page > 0 else "app.bell"), "index": -1}
                    )
                )

                page.append_text(
                    Text.assemble(
                        (f" Page {self.page + 1}/{len(self.pages)} ", "yellow")  # type: ignore
                    )
                )

                page.append_text(
                    Text.assemble(
                        (
                            "Next ->",
                            ("grey" if self.highlighted == -2 else "white")
                            if self.page + 1 < len(self.pages) else "#4f4f4f"  # type: ignore
                        ),
                        meta={
                            "@click": (
                                "app.next_page" if self.page + 1 < len(self.pages) else "app.bell"  # type: ignore
                            ),
                            "index": -2
                        }
                    )
                )
            self._text = Panel(page, title=self.so.sidebar_title)

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
        SO_RESULTS.index = index
        self.index = index

        await self.update_body()

    async def action_next_question(self) -> None:
        """Go to the next question."""
        if self.index + 1 < len(SO_RESULTS):
            self.viewing_traceback: bool = False
            self.index += 1
            await self.update_body()
            self.sidebar.index = self.index
            SO_RESULTS.index = self.index

    async def action_prev_question(self) -> None:
        """Go to the previous question."""
        if self.index:
            self.viewing_traceback = False
            self.index -= 1
            await self.update_body()
            self.sidebar.index = self.index
            SO_RESULTS.index = self.index

    async def action_next_page(self) -> None:
        """Set page"""
        self.sidebar.page += 1

    async def action_prev_page(self) -> None:
        """Set page"""
        self.sidebar.page -= 1

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


if __name__ == "__main__":
    try:
        1 / 0
    except ZeroDivisionError as e:
        trace = Trace(e)
    engine = SearchEngine(trace)
    so = StackOverflow.from_trace(trace=trace, clear_cache=False)
    store_results_in_module(
        trace=trace,
        so_results=so,
        search_engine=engine,
    )
    TextualDisplay().run()
