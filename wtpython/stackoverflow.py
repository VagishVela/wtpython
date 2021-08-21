from __future__ import annotations

from textwrap import dedent

from requests_cache import CachedSession
from requests_cache.backends import FileCache

from wtpython import SearchError
from wtpython.formatters import PythonCodeConverter, rich_link
from wtpython.settings import (
    REQUEST_CACHE_DURATION, REQUEST_CACHE_LOCATION, SO_MAX_RESULTS
)
from wtpython.trace import Trace

SO_API = "https://api.stackexchange.com/2.3"
# https://api.stackexchange.com/docs/filters
# To create a custom filter, use https://api.stackexchange.com/docs/create-filter
# This filter returns the question or answer body in addition to meta data.
SO_FILTER = "!6VvPDzQ)xXOrL"
# These parameters are applied to all question and answer queries.
DEFAULT_PARAMS: dict[str, str] = {
    "site": "stackoverflow",
    "filter": SO_FILTER,
    "order": "desc",
}
# List of items to add to all queries.
DEFAULT_QUERIES = ["python"]


class CachedResponse:
    """Class for caching web queries.

    This class should be extended by any class that makes web queries.
    The `cache_key` should be defined to avoid caching conflicts.
    """

    cache_key = 'wtpython'

    def __init__(self, clear_cache: bool = False) -> None:
        """Initialize the session and cache."""
        self.session = CachedSession(
            self.cache_key,
            backend=FileCache(REQUEST_CACHE_LOCATION),
            expire_after=REQUEST_CACHE_DURATION,
        )
        if clear_cache:
            self.session.cache.clear()

    def __del__(self) -> None:
        """Close the session on exit."""
        self.session.close()


class StackOverflowAnswer:
    """Class for visualizing StackOverflow answers.

    This class should only be called by the `StackOverflowQuestion` class.
    Answers should only be visible in the main TUI window, so `sidebar` and
    `no_display` are not implemented.
    """

    def __init__(self, data: dict) -> None:
        """Store the json for the answer."""
        self.data = data

    @property
    def answer_accepted(self) -> str:
        """Return a string indicating if the answer is accepted."""
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
        """Store the json for the question."""
        self.ix = ix
        self.data = data
        self.answers: list[StackOverflowAnswer] = []

    @property
    def num_answers(self) -> str:
        """Return a string indicating the number of answers."""
        if self.data['answer_count'] == 1:
            return '1 Answer'
        else:
            return f'{self.data["answer_count"]} Answers'

    @property
    def answer_accepted(self) -> str:
        """Return a string indicating if the question has an accepted answer."""
        return ' ✔️ ' if self.data['is_answered'] else ''

    def sidebar(self, ix: int) -> str:
        """Render information for sidebar mode."""
        color = 'yellow' if ix == self.ix else 'white'
        text = (
            f"[{color}]"
            f"#{self.ix + 1} "
            f"[bold]Score {self.data['score']}[/]"
            f"{self.answer_accepted} - {self.data['title']}"
            f"[/]"
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

    This class is responsible for the api calls and managing the results.
    """

    cache_key = 'stackoverflow'

    def __init__(self, query: str, clear_cache: bool = False) -> None:
        """Search stackoverflow api for the defined query.

        self.index is used to track the current question. Initialization
        will search for questions and fetch the associated answers.
        """
        super().__init__(clear_cache=clear_cache)
        self.index = 0
        self._query = query
        self.questions = [StackOverflowQuestion(ix, item) for ix, item in enumerate(self.get_questions())]
        self.get_answers()

    @classmethod
    def from_trace(cls, trace: Trace, clear_cache: bool = False) -> StackOverflow:
        """Initialize from traceback.

        Will search for questions based on the full error message. If no results,
        this will fall back on just the error type. If no results, this will raise
        a SearchError.

        Since we are caching the results, the return statements should not
        warrant extra api requests.
        """
        questions = cls(trace.error, clear_cache).get_questions()
        if questions:
            return cls(trace.error, clear_cache)

        questions = cls(trace.etype, clear_cache).get_questions()
        if questions:
            cls(trace.etype, clear_cache)

        raise SearchError(f"No StackOverflow results for {trace.error}")

    def get_questions(self) -> dict:
        """Get StackOverflow questions.

        https://api.stackexchange.com/docs/advanced-search
        """
        endpoint = f"{SO_API}/search/advanced"
        params = {
            "q": ' '.join([*DEFAULT_QUERIES, self._query]),
            "answers": 1,
            "pagesize": SO_MAX_RESULTS,
            **DEFAULT_PARAMS,
        }
        response = self.session.get(endpoint, params=params)
        return response.json()['items']

    def get_answers(self) -> None:
        """Get answers for this question.

        https://api.stackexchange.com/docs/answers-on-questions
        The answers for all questions are fetched with one api call. Answers
        are assigned to the questions based on the asssociated question id.
        """
        question_ids = ";".join([
            str(q.data['question_id'])
            for q in self.questions
        ])
        endpoint = f"{SO_API}/questions/{question_ids}/answers"
        params = {
            "sort": "activity",
            **DEFAULT_PARAMS,
        }
        response = self.session.get(endpoint, params=params)
        answers = response.json()['items']

        for question in self.questions:
            question.answers = [
                StackOverflowAnswer(answer)
                for answer in answers
                if answer['question_id'] == question.data['question_id']
            ]

    def sidebar(self) -> list[str]:
        """Render information for sidebar mode.

        consolodate sidebar displays for all objects. ix is used to determine
        if the item is the current one.
        """
        return [item.sidebar(self.index) for item in self.questions]

    def display(self) -> str:
        """Render information for display mode.

        Get the display for the current item.
        """
        return self.questions[self.index].display()

    def no_display(self) -> str:
        """Render information for no-display mode."""
        return "\n".join([item.no_display() for item in self.questions])
