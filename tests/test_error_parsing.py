import pytest
import toml

from pytui.parser import parse_stacktrace
from pytui.settings import BASE_DIR

TEST_DATA_DIR = BASE_DIR.parent / 'tests' / 'data'


for_each_example_stacktrace = pytest.mark.parametrize(
    "example_stacktrace",
    [
        toml.load(example)
        for example
        in TEST_DATA_DIR.glob('*.toml')
    ]
)


@for_each_example_stacktrace
def test_parsing_has_correct_format(example_stacktrace: dict) -> None:
    """Ensure parse_stacktrace provides dict."""
    parsed = parse_stacktrace(example_stacktrace['traceback'])
    assert list(parsed.keys()) == ['error_message', 'files', 'packages']  # noqa: S101


@for_each_example_stacktrace
def test_correct_error_message(example_stacktrace: dict) -> None:
    """Ensure that the error message is correctly capturerd."""
    parsed = parse_stacktrace(example_stacktrace['traceback'])
    assert parsed['error_message'] == example_stacktrace['error_message']  # noqa: S101


@for_each_example_stacktrace
def test_correct_file_references(example_stacktrace: dict) -> None:
    """Ensure file information was extracted correctly."""
    parsed = parse_stacktrace(example_stacktrace['traceback'])
    for field in ['file', 'line', 'method']:
        found = [i[field] for i in parsed['files']]
        expected = [i[field] for i in example_stacktrace['files']]
        assert found == expected  # noqa: S101


@for_each_example_stacktrace
def test_correct_packages(example_stacktrace: dict) -> None:
    """Ensure that packages involved are correrctly identified."""
    parsed = parse_stacktrace(example_stacktrace['traceback'])
    assert set(parsed['packages']) == set(example_stacktrace['packages'])  # noqa: S101
