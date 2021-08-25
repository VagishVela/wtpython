from __future__ import annotations

from textwrap import dedent
from typing import Optional

from rich.text import Text

from wtpython.exceptions import SearchError
from wtpython.formatters import PythonCodeConverter, rich_link
from wtpython.settings import SO_MAX_RESULTS

from .cache import CachedResponse
from .trace import Trace


class StackOverflowAnswer:
    """Class for visualizing StackOverflow answers.

    This class should only be called by the `StackOverflowQuestion` class.
    Answers should only be visible in the main TUI window, so `sidebar` and
    `no_display` are not implemented.
    """

    def __init__(self, data: dict) -> None:
        """Store the json for the answer.

        Args:
            data: The json data for the answer provided by the API.
        """
        self.data = data

    @property
    def answer_accepted(self) -> str:
        """String indicating if the answer is accepted."""
        return ' ✔️ ' if self.data['is_accepted'] else ''

    def display(self) -> str:
        """Render information for display mode."""
        converter = PythonCodeConverter()

        text = dedent(f"""
        ---
        ### Answer Score {self.data['score']}{self.answer_accepted}
        ---

        {converter.convert(self.data['body'])}
        """)
        return text.lstrip()


class StackOverflowQuestion:
    """Class for visualizing StackOverflow questions.

    This class should only be called by the `StackOverflow` class.
    This handles the display of questions and associated answers.
    """

    def __init__(self, ix: int, data: dict) -> None:
        """Store the json for the question.

        Args:
            ix: The index of the question in the list of questions.
            data: The json data for the question provided by the API.

        Returns:
            None
        """
        self.ix = ix
        self.data = data
        self.answers: list[StackOverflowAnswer] = []

    @property
    def num_answers(self) -> str:
        """Human readable string indicating the number of answers."""
        if self.data['answer_count'] == 1:
            return '1 Answer'
        else:
            return f'{self.data["answer_count"]} Answers'

    @property
    def answer_accepted(self) -> str:
        """String indicating if the question has an accepted answer."""
        return ' ✔️ ' if self.data['is_answered'] else ''

    @property
    def url(self) -> str:
        """The url for the question."""
        return self.data['link']

    def sidebar(self, ix: int, highlighted: Optional[int]) -> Text:
        """Render information for sidebar mode.

        Args:
            ix: The index of the active question. Used to determine highlighting.
            highlighted: The index of the hovered question. Used to determine highlighting.

        Returns:
            A rich text object for the sidebar.
        """
        color = 'yellow' if ix == self.ix else ('grey' if highlighted == self.ix else 'white')

        text = Text.assemble(
            (f"#{self.ix + 1} ", color),
            (f"Score {self.data['score']}", f"{color} bold"),
            (f"{self.answer_accepted} - {self.data['title']}", color),
        )
        return text

    def display(self) -> str:
        """Render information for display mode."""
        converter = PythonCodeConverter()

        text = dedent(f"""
        Score {self.data['score']} | {self.data['title']}
        {converter.convert(self.data['body'])}
        """)
        for answer in self.answers:
            text += answer.display()

        return text

    def no_display(self) -> str:
        """Render information for no-display mode."""
        return dedent(f"""
            Score {self.data['score']} | {self.data['title']}
            {rich_link(self.data['link'])} {self.num_answers} {self.answer_accepted}
        """).lstrip()


class StackOverflow(CachedResponse):
    """Manage results from Stack Overflow.

    This class can be instantiated by passing a query to the constructor,
    or the classmethod `from_trace` will accept a Trace object.

    This class is responsible for the api calls and managing the results.
    The StackOverflowQuestion and StackOverflowAnswer classes should not
    be called outside of this class.

    The main public functions of this class are:
        sidebar: render information for textual sidebar. Item with self.index
            will be highlighted.
        display: render information for textual scrollview. This will display
            the question and all answers for the question with self.index.
        no_display: render information for no-display mode. Dumps all questions.

    Filter: https://api.stackexchange.com/docs/filters
    Create a filter: https://api.stackexchange.com/docs/create-filter
    This filter returns the question or answer body in addition to meta data.
    """

    api = "https://api.stackexchange.com/2.3"
    cache_key = 'stackoverflow'
    sidebar_title = "Questions"
    default_params: dict[str, str] = {
        "site": "stackoverflow",
        "filter": "!6VvPDzQ)xXOrL",
        "order": "desc",
    }

    def __init__(self, query: str = '', clear_cache: bool = False) -> None:
        """Search stackoverflow api for the defined query.

        self.index is used to track the current question. Initialization
        will search for questions and fetch the associated answers.

        Args:
            query: The query to search for.
            clear_cache: If True, clear the cache before searching.

        Returns:
            StackOverflow object.
        """
        super().__init__(clear_cache=clear_cache)
        self._query = query
        self.index = 0
        self.highlighted = None
        self.questions = [StackOverflowQuestion(ix, item) for ix, item in enumerate(self._get_questions())]
        self._get_answers()

    def __len__(self) -> int:
        """Return the number of questions found."""
        return len(self.questions)

    def __bool__(self) -> bool:
        """Return whether the query has results."""
        return bool(self.questions)

    @classmethod
    def from_trace(cls, trace: Trace, clear_cache: bool = False) -> StackOverflow:
        """Initialize from traceback.

        Will search for questions based on the full error message. If no results,
        this will fall back on just the error type. If no results, this will raise
        a SearchError.

        Args:
            trace: The wtpython Trace object.
            clear_cache: If True, clear the cache before searching.

        Returns:
            StackOverflow object.
        """
        for query in [trace.error, trace.etype]:
            instance = cls(query, clear_cache)
            if instance:
                return instance

        raise SearchError(f"No StackOverflow results for {trace.error}")

    def _get_questions(self) -> dict:
        """Get StackOverflow questions.

        https://api.stackexchange.com/docs/advanced-search
        defaults is a list of items to include with every request.
        """
        endpoint = f"{StackOverflow.api}/search/advanced"
        defaults = ['python']
        params = {
            "q": ' '.join([*defaults, self._query]),
            "answers": 1,
            "pagesize": SO_MAX_RESULTS,
            **StackOverflow.default_params,
        }
        response = self.session.get(endpoint, params=params)
        return response.json()['items']

    def _get_answers(self) -> None:
        """Get answers for this question.

        https://api.stackexchange.com/docs/answers-on-questions
        The answers for all questions are fetched with one api call. Answers
        are assigned to the questions based on the asssociated question id.
        """
        question_ids = ";".join([
            str(q.data['question_id'])
            for q in self.questions
        ])
        endpoint = f"{StackOverflow.api}/questions/{question_ids}/answers"
        params = {
            "sort": "activity",
            **StackOverflow.default_params,
        }
        response = self.session.get(endpoint, params=params)
        answers = response.json()['items']

        for question in self.questions:
            question.answers = [
                StackOverflowAnswer(answer)
                for answer in answers
                if answer['question_id'] == question.data['question_id']
            ]

    @property
    def active_url(self) -> str:
        """Return the url for the current question."""
        if self.questions:
            return self.questions[self.index].url
        return "https://stackoverflow.com/search?q={self._query}"

    def sidebar(self) -> list[Text]:
        """Render information for sidebar mode.

        consolodate sidebar displays for all objects. ix is used to determine
        if the item is the current one.
        """
        return [q.sidebar(self.index, self.highlighted) for q in self.questions]

    def display(self) -> str:
        """Render information for display mode.

        Get the display for the current item.
        """
        if self.questions:
            return self.questions[self.index].display()
        return "Sorry, we could not find any results."

    def no_display(self) -> str:
        """Render information for no-display mode."""
        return "\n".join([q.no_display() for q in self.questions])
