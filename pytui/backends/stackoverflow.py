from typing import List

import requests

from pytui.settings import SO_FILTER


class StackOverflowAnswer:
    """Stack overflow answer object"""

    def __init__(self, answer_json: dict):
        self.raw_json: dict = answer_json
        self.is_accepted: bool = answer_json["is_accepted"]
        self.score: int = answer_json["score"]
        self.answer_id: int = answer_json["answer_id"]
        self.body: str = answer_json["body"]


class StackOverflowQuestion:
    """Stack overflow question object"""

    def __init__(self, question_json: dict, answer_json: dict):
        self.raw_json: dict = question_json
        self.question_id: int = question_json["question_id"]
        self.link: str = question_json["link"]
        self.title: str = question_json["title"]
        self.score: int = question_json["score"]
        self.body: str = question_json["body"]
        self.answers: List[StackOverflowAnswer] = [StackOverflowAnswer(x) for x in answer_json["items"]]


class StackOverflowFinder:
    """Get results from Stack Overflow"""

    def __init__(self):
        # Initialize SE API object...
        self.session = requests.session()
        pass

    def search(self, error_message: str, max_results: int = 5) -> List[StackOverflowQuestion]:
        """Search Stack Overflow with the initialized SE API object"""
        result = self.session.get(
            "https://api.stackexchange.com/2.3/search",
            params={
                "pagesize": max_results,
                "order": "desc",
                "sort": "relevance",
                "tagged": "python",
                "intitle": error_message.split(" ")[0].strip(":"),
                "site": "stackoverflow",
                "filter": SO_FILTER,
            },
        )
        data = result.json()
        answers = []
        for i in data["items"]:
            if i["is_answered"]:
                answers.append([
                    i,
                    self.session.get(
                        f'https://api.stackexchange.com/{i["question_id"]}/answers',
                        params={
                            "order": "desc",
                            "sort": "activity",
                            "site": "stackoverflow",
                            "filter": SO_FILTER,
                        }
                    ).json(),
                ])

        return [StackOverflowQuestion(x[0], x[1]) for x in answers]
