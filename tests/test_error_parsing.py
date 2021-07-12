import pytest
import toml

from pytui.parser import parse_stacktrace


@pytest.fixture
def sample_error(shared_datadir: pytest.fixture) -> dict:
    """Iterate through all example cases in data directory."""
    for file in shared_datadir.glob("*.toml"):
        yield toml.load(file)


def test_parsing_has_correct_format(sample_error: pytest.fixture) -> None:
    """Ensure parse_stacktrace provides dict."""
    parsed = parse_stacktrace(sample_error['traceback'])
    assert list(parsed.keys()) == ['error_message', 'files', 'packages']  # noqa: S101
    for value in parsed.values():
        assert value  # noqa: S101


def test_correct_error_message(sample_error: pytest.fixture) -> None:
    """Ensure that the error message is correctly capturerd."""
    parsed = parse_stacktrace(sample_error['traceback'])
    assert parsed['error_message'] == sample_error['error_message']  # noqa: S101


def test_correct_file_references(sample_error: pytest.fixture) -> None:
    """Ensure file information was extracted correctly."""
    parsed = parse_stacktrace(sample_error['traceback'])
    for field in ['file', 'line', 'method']:
        found = [i[field] for i in parsed['files']]
        expected = [i[field] for i in sample_error['files']]
        assert found == expected  # noqa: S101


def test_correct_packages(sample_error: pytest.fixture) -> None:
    """Ensure that packages involved are correrctly identified."""
    parsed = parse_stacktrace(sample_error['traceback'])
    assert set(parsed['packages']) == set(sample_error['packages'])  # noqa: S101
