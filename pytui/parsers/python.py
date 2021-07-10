from typing import List


class PythonParser:
    """Parse the python output and get errors"""

    def __init__(self, all_output: str):
        self.all_output = all_output

    def parse_error(self) -> List[str]:
        """Return errors from python output"""
        return self.all_output.split('\n')[-1]
