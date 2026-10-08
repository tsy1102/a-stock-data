"""Project-local temporary directory configuration."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def configure_project_temp() -> Path:
    """Point Python and child processes at the project temp directory.

    ``ASTOCK_TEMP_DIR`` is the explicit override. Otherwise the repository's
    ``.tmp`` directory is used, including for direct ``python main.py`` runs.
    """
    configured = os.environ.get("ASTOCK_TEMP_DIR", "").strip()
    if configured:
        temp_path = Path(configured).expanduser()
    else:
        temp_path = Path(__file__).resolve().parents[1] / ".tmp"

    temp_path.mkdir(parents=True, exist_ok=True)
    resolved = temp_path.resolve()
    temp_value = str(resolved)
    for variable in ("TEMP", "TMP", "TMPDIR"):
        os.environ[variable] = temp_value
    tempfile.tempdir = temp_value
    return resolved


__all__ = ["configure_project_temp"]
