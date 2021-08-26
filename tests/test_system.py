"""Tests for the core of WTPython."""
import sys
from contextlib import contextmanager
from typing import Iterator

import pytest

import wtpython
from wtpython.__main__ import parse_arguments


@contextmanager
def update_argv(args: list) -> Iterator[None]:
    """Update sys.argv."""
    orig, sys.argv = sys.argv, args
    yield
    sys.argv = orig


def test_version() -> None:
    """Test Version is Correct."""
    assert wtpython.__version__ == "0.1"


def test_default_parse_args() -> None:
    """Simple test to demonstrate how to test the arg parser."""
    args = ['wtpython', __file__]
    with update_argv(args):
        parsed = parse_arguments()

    assert parsed.get('no-display') is None
    assert parsed.get('copy_error') == False
    assert parsed.get('clear_cache') == False
    assert parsed.get('args') == [__file__]


@pytest.mark.parametrize("args", [
    ['wtpython', '--no-display', __file__],
    ['wtpython', '-n', __file__],
])
def test_no_display_option(args: list) -> None:
    """Test that the no-display option is set."""
    with update_argv(args):
        parsed = parse_arguments()
    assert parsed.get('no_display') == True


@pytest.mark.parametrize("args", [
    ['wtpython', '--copy-error', __file__],
    ['wtpython', '-c', __file__],
])
def test_copy_error_option(args: list) -> None:
    """Test that the copy-error option is set."""
    with update_argv(args):
        parsed = parse_arguments()
    assert parsed.get('copy_error') == True


@pytest.mark.parametrize("args", [
    ['wtpython', '--clear-cache', __file__],
])
def test_clear_cache_option(args: list) -> None:
    """Test that the clear-cache option is set."""
    with update_argv(args):
        parsed = parse_arguments()
    assert parsed.get('clear_cache') == True


@pytest.mark.parametrize("args", [
    ['wtpython'],
    ['wtpython', '-c'],
    ['wtpython', '-n'],
])
def test_exit_on_no_script(args: list) -> None:
    """Test script exits if no script is provided."""
    with update_argv(args):
        with pytest.raises(SystemExit):
            parse_arguments()


def test_exit_on_non_existent_file() -> None:
    """Test script exits when file does not exist."""
    args = ['wtpython', 'non-existent-file.py']
    with update_argv(args):
        with pytest.raises(SystemExit):
            parse_arguments()
