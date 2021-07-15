import wtpython


def test_version() -> None:
    """Test Version is Correct"""
    assert wtpython.__version__ == "0.0.1"  # noqa: S101
