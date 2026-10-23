"""Read field-capture JSON from the working tree or its local cold archive."""

from __future__ import annotations

import json
import os
import re
import shutil
import zipfile
import importlib
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

_package_prefix = f"{__package__}." if __package__ else ""
_retention_module = importlib.import_module(f"{_package_prefix}capture_retention")
MIN_CAPTURE_DATE = _retention_module.MIN_CAPTURE_DATE

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIELD_VERIFICATION_ROOT = PROJECT_ROOT / "docs" / "field_verification"
ARCHIVE_PATH = PROJECT_ROOT / ".archive" / "field_verification_raw_cold.zip"
_DATE_DIR_RE = re.compile(r"^\d{8}$")


def _capture_date_for_path(path: str | Path) -> date | None:
    target = Path(os.path.abspath(os.fspath(path)))
    root = Path(os.path.abspath(FIELD_VERIFICATION_ROOT))
    try:
        relative = target.relative_to(root)
    except ValueError:
        return None
    if not relative.parts or not _DATE_DIR_RE.fullmatch(relative.parts[0]):
        return None
    try:
        return date(
            int(relative.parts[0][:4]),
            int(relative.parts[0][4:6]),
            int(relative.parts[0][6:8]),
        )
    except ValueError:
        return None


def _reject_pre_retention_path(path: str | Path) -> None:
    capture_date = _capture_date_for_path(path)
    if capture_date is not None and capture_date < MIN_CAPTURE_DATE:
        raise FileNotFoundError(
            f"capture date {capture_date:%Y%m%d} is before retention floor "
            f"{MIN_CAPTURE_DATE:%Y%m%d}: {path}"
        )


def _capture_prefix(folder: Path) -> str | None:
    _reject_pre_retention_path(folder)
    try:
        relative = folder.resolve().relative_to(FIELD_VERIFICATION_ROOT.resolve())
    except ValueError:
        return None
    if len(relative.parts) != 1 or not _DATE_DIR_RE.fullmatch(relative.name):
        return None
    return f"docs/field_verification/{relative.as_posix()}/"


def _archived_members(prefix: str) -> list[str]:
    if not ARCHIVE_PATH.is_file():
        return []
    with zipfile.ZipFile(ARCHIVE_PATH) as archive:
        return sorted(
            name
            for name in archive.namelist()
            if name.startswith(prefix)
            and "/" not in name[len(prefix) :]
            and name[len(prefix) :].startswith("raw_")
            and name.endswith(".json")
        )


def raw_capture_sources(folder: Path) -> set[str]:
    """Return source names available as plain files or archived JSON."""
    _reject_pre_retention_path(folder)
    sources = {
        path.name[len("raw_") : -len(".json")]
        for path in folder.iterdir()
        if path.is_file() and path.name.startswith("raw_") and path.name.endswith(".json")
    }
    prefix = _capture_prefix(folder)
    if prefix is not None:
        sources.update(
            member[len(prefix) + len("raw_") : -len(".json")]
            for member in _archived_members(prefix)
        )
    return sources


def read_capture_json(path: str | Path) -> Any:
    """Read a capture JSON, falling back to the matching archive member."""
    target = Path(path)
    _reject_pre_retention_path(target)
    if target.is_file():
        with target.open("r", encoding="utf-8") as stream:
            return json.load(stream)

    try:
        relative = target.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise FileNotFoundError(target) from exc
    prefix = "docs/field_verification/"
    if not relative.startswith(prefix):
        raise FileNotFoundError(target)
    if not ARCHIVE_PATH.is_file():
        raise FileNotFoundError(target)
    try:
        with zipfile.ZipFile(ARCHIVE_PATH) as archive, archive.open(relative) as stream:
            return json.load(stream)
    except KeyError as exc:
        raise FileNotFoundError(target) from exc


def materialize_capture_folder(folder: str | Path) -> int:
    """Restore archived raw JSON files for a capture before it is re-collected."""
    capture_dir = Path(folder).resolve()
    _reject_pre_retention_path(capture_dir)
    prefix = _capture_prefix(capture_dir)
    if prefix is None or not ARCHIVE_PATH.is_file():
        return 0

    restored = 0
    with zipfile.ZipFile(ARCHIVE_PATH) as archive:
        for member in _archived_members(prefix):
            relative_parts = PurePosixPath(member).parts
            target = (PROJECT_ROOT / Path(*relative_parts)).resolve()
            try:
                target.relative_to(capture_dir)
            except ValueError as exc:
                raise ValueError(f"archive member escapes capture directory: {member}") from exc
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            restored += 1
    return restored
