import pytest
import toml

from pytui.parse_errors import parse_err


@pytest.fixture
def sample_error(shared_datadir: pytest.fixture) -> dict:
    """Iterate through all example cases in data directory."""
    for file in shared_datadir.glob("*.toml"):
        yield toml.load(file)


def test_correct_error_message(sample_error: pytest.fixture) -> None:
    """Ensure that the error message is correctly capturerd."""
    error_msg, _ = parse_err(sample_error['traceback'])
    assert error_msg == sample_error['error_message']  # noqa: S101


def test_correct_packages(sample_error: pytest.fixture) -> None:
    """Ensure that packages involved are correrctly identified."""
    _, packages = parse_err(sample_error['traceback'])
    assert list(packages) == list(sample_error['error_packages'])  # noqa: S101
