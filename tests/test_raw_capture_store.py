from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from scripts import raw_capture_store as store


@pytest.fixture
def capture_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    project_root = tmp_path / "project"
    field_root = project_root / "docs" / "field_verification"
    archive_path = project_root / ".archive" / "field_verification_raw_cold.zip"
    field_root.mkdir(parents=True)
    monkeypatch.setattr(store, "PROJECT_ROOT", project_root)
    monkeypatch.setattr(store, "FIELD_VERIFICATION_ROOT", field_root)
    monkeypatch.setattr(store, "ARCHIVE_PATH", archive_path)
    return project_root, field_root


def test_read_capture_json_rejects_existing_pre_retention_file(
    capture_roots: tuple[Path, Path],
) -> None:
    _, field_root = capture_roots
    old_path = field_root / "20261014" / "raw_push2.json"
    old_path.parent.mkdir()
    old_path.write_text('{"secret": "old sample"}', encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="before retention floor 20261015"):
        store.read_capture_json(old_path)


def test_read_capture_json_does_not_fall_back_to_pre_retention_archive_member(
    capture_roots: tuple[Path, Path],
) -> None:
    project_root, _ = capture_roots
    store.ARCHIVE_PATH.parent.mkdir()
    with zipfile.ZipFile(store.ARCHIVE_PATH, "w") as archive:
        archive.writestr(
            "docs/field_verification/20261014/raw_push2.json",
            '{"secret": "old sample"}',
        )
    old_path = project_root / "docs" / "field_verification" / "20261014" / "raw_push2.json"

    with pytest.raises(FileNotFoundError, match="before retention floor 20261015"):
        store.read_capture_json(old_path)


def test_retained_capture_is_read_from_working_tree(
    capture_roots: tuple[Path, Path],
) -> None:
    _, field_root = capture_roots
    retained_path = field_root / "20261015" / "raw_push2.json"
    retained_path.parent.mkdir()
    retained_path.write_text('{"ok": true}', encoding="utf-8")

    assert store.read_capture_json(retained_path) == {"ok": True}


def test_retained_capture_can_be_read_from_archive(
    capture_roots: tuple[Path, Path],
) -> None:
    project_root, field_root = capture_roots
    folder = field_root / "20261015"
    folder.mkdir()
    store.ARCHIVE_PATH.parent.mkdir()
    with zipfile.ZipFile(store.ARCHIVE_PATH, "w") as archive:
        archive.writestr(
            "docs/field_verification/20261015/raw_push2.json",
            '{"ok": true}',
        )
    archived_path = project_root / "docs" / "field_verification" / "20261015" / "raw_push2.json"

    assert store.read_capture_json(archived_path) == {"ok": True}
    assert store.raw_capture_sources(folder) == {"push2"}


def test_pre_retention_folder_cannot_be_listed_or_materialized(
    capture_roots: tuple[Path, Path],
) -> None:
    _, field_root = capture_roots
    old_folder = field_root / "20261014"
    old_folder.mkdir()
    (old_folder / "raw_push2.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="before retention floor 20261015"):
        store.raw_capture_sources(old_folder)
    with pytest.raises(FileNotFoundError, match="before retention floor 20261015"):
        store.materialize_capture_folder(old_folder)
