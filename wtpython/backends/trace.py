import traceback
from pathlib import Path
from types import TracebackType
from typing import Optional

from rich.traceback import Traceback


class Trace:
    """Class for handling the formatting and display of tracebacks."""

    def __init__(self, exc: Exception) -> None:
        """Store key parts to traceback."""
        self._etype = type(exc)
        self._value = exc
        self._tb = Trace.trim_exception_traceback(exc.__traceback__)

    @staticmethod
    def trim_exception_traceback(tb: Optional[TracebackType]) -> Optional[TracebackType]:
        """
        Trim the traceback to remove extra frames

        Because of the way we are currently running the code, any traceback
        created during the execution of the application will be include the
        stack frames of this application. This function removes all the stack
        frames from the beginning of the traceback until we stop seeing `runpy`.
        """
        seen_runpy = False
        while tb is not None:
            cur = tb.tb_frame
            filename = Path(cur.f_code.co_filename).name
            if filename == "runpy.py":
                seen_runpy = True
            elif seen_runpy and filename != "runpy.py":
                break
            tb = tb.tb_next

        return tb

    @property
    def etype(self) -> str:
        """Error Type."""
        return self._etype.__name__

    @property
    def error(self) -> str:
        """Error type and value."""
        _error = "".join(traceback.format_exception_only(self._etype, self._value)).strip()
        error_lines = _error.split("\n")
        if len(error_lines) > 1:
            _error = error_lines[-1]
        return _error

    @property
    def traceback(self) -> str:
        """Full traceback."""
        return "".join(traceback.format_exception(self._etype, self._value, self._tb))

    @property
    def rich_traceback(self) -> Traceback:
        """Rich formatted traceback."""
        return Traceback.from_exception(self._etype, self._value, self._tb)
