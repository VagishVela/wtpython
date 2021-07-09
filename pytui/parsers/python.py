

class PythonParser:
    def __init__(self, all_output):
        self.all_output = all_output

    def parse_error(self):
        return self.all_output.split('\n')[-1]