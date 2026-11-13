"""Per-process UTF-8 output setup without changing persistent user settings."""

from __future__ import annotations

import sys


def ensure_utf8_stdio() -> None:
    """Set this process's stdout and stderr to UTF-8 when supported."""
    for _stream in (sys.stdout, sys.stderr):
        if _stream is not None and hasattr(_stream, "reconfigure"):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
