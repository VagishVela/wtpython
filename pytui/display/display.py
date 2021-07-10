from typing import List


class Display:
    """Display with browser of stack overflow for finding results"""

    def __init__(self, error_message: str, search_results: List[str]):
        self.error_message = error_message
        self.search_result = search_results

    def start(self) -> None:
        """Open window... do stuff"""
        pass
