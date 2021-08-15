import html
from typing import List

from requests_cache import CachedSession
from requests_cache.backends import FileCache

from wtpython import SearchError
from wtpython.settings import (
    REQUEST_CACHE_DURATION, REQUEST_CACHE_LOCATION, SO_API, SO_FILTER,
    SO_MAX_RESULTS
)


class StackOverflowAnswer:
    """Stack overflow answer object."""

    def __init__(self, answer_json: dict):
        """Store results form answer object.

        The answer object contains the following fields:
        - answer_id
        - body
        - content_license
        - creation_date
        - is_accepted
        - last_activity_date
        - question_id
        - score
        """
        self.raw_json: dict = answer_json
        self.is_accepted: bool = answer_json["is_accepted"]
        self.score: int = answer_json["score"]
        self.answer_id: int = answer_json["answer_id"]
        self.body: str = answer_json["body"]


class StackOverflowQuestion:
    """Stack overflow question object.

    The question object (question_json) contains the following fields:
    - answer_count
    - content_license
    - creation_date
    - is_answered
    - last_activity_date
    - link
    - owner
    - question_id
    - score
    - view_count
    """

    def __init__(self, question_json: dict, answer_json: dict):
        self.raw_json: dict = question_json
        self.question_id: int = question_json["question_id"]
        self.link: str = question_json["link"]
        self.title: str = html.unescape(question_json["title"])
        self.score: int = question_json["score"]
        self.body: str = question_json["body"]

        self.answers: List[StackOverflowAnswer] = [StackOverflowAnswer(x) for x in answer_json["items"]]
        self.answers.sort(key=lambda x: (x.is_accepted, x.score), reverse=True)

    def __str__(self):
        return f"{self.title}\n{self.link}"


class StackOverflowFinder:
    """Manage results from Stack Overflow."""

    def __init__(self, clear_cache: bool = False):
        self.session = CachedSession(
            'stackoverflow',
            backend=FileCache(REQUEST_CACHE_LOCATION),
            expire_after=REQUEST_CACHE_DURATION,
        )
        if clear_cache:
            self.session.cache.clear()

    def get_answers(self, question: dict) -> dict:
        """Get all answers for a question."""
        params = {
            "order": "desc",
            "sort": "activity",
            "site": "stackoverflow",
            "filter": SO_FILTER,
        }
        response = self.session.get(f"{SO_API}/questions/{question['question_id']}/answers", params=params)
        return response.json()

    def search(self, error_message: str, max_results: int = SO_MAX_RESULTS) -> List[StackOverflowQuestion]:
        """Search Stack Overflow for relevant questions."""
        params = {
            "pagesize": max_results,
            "order": "desc",
            "sort": "relevance",
            "tagged": "python",
            "intitle": error_message,
            "site": "stackoverflow",
            "filter": SO_FILTER,
        }
        response = self.session.get(f"{SO_API}/search", params=params)
        if not response.ok:
            raise SearchError("Error fetching StackOverflow response: {data}")

        questions = response.json()

        data = [
            StackOverflowQuestion(question, self.get_answers(question))
            for question in questions["items"]
            if question["is_answered"]
        ]

        self.session.close()
        return data
