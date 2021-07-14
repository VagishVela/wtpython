import pytest
import toml

from wtpython.core import parse_traceback
from wtpython.settings import BASE_DIR

TEST_DATA_DIR = BASE_DIR.parent / 'tests' / 'data'


for_each_example_traceback = pytest.mark.parametrize(
    "example_traceback",
    [
        toml.load(example)
        for example
        in TEST_DATA_DIR.glob('*.toml')
    ]
)


@for_each_example_traceback
def test_parsing_has_correct_format(example_traceback: dict) -> None:
    """Ensure parse_traceback provides dict."""
    parsed = parse_traceback(example_traceback['traceback'])
    assert list(parsed.keys()) == ['error_message', 'files', 'packages', 'traceback']  # noqa: S101


@for_each_example_traceback
def test_correct_error_message(example_traceback: dict) -> None:
    """Ensure that the error message is correctly capturerd."""
    parsed = parse_traceback(example_traceback['traceback'])
    assert parsed['error_message'] == example_traceback['error_message']  # noqa: S101


@for_each_example_traceback
def test_correct_file_references(example_traceback: dict) -> None:
    """Ensure file information was extracted correctly."""
    parsed = parse_traceback(example_traceback['traceback'])
    for field in ['file', 'line', 'method']:
        found = [i[field] for i in parsed['files']]
        expected = [i[field] for i in example_traceback['files']]
        assert found == expected  # noqa: S101


@for_each_example_traceback
def test_correct_packages(example_traceback: dict) -> None:
    """Ensure that packages involved are correrctly identified."""
    parsed = parse_traceback(example_traceback['traceback'])
    assert set(parsed['packages']) == set(example_traceback['packages'])  # noqa: S101
