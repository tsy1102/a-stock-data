"""Check Black formatting through its Python API to avoid the Windows CLI hang."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

import black

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRUNED_DIRS = {
    ".git",
    ".pytest_cache",
    ".tmp",
    ".venv",
    "__pycache__",
    "logs",
    "reports",
    "snapshots",
}


def _project_black_config() -> (
    tuple[black.FileMode, re.Pattern[str], re.Pattern[str], re.Pattern[str]]
):
    config = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    options = config.get("tool", {}).get("black", {})
    target_versions = {
        black.TargetVersion[name.upper()] for name in options.get("target-version", ["py311"])
    }
    mode = black.FileMode(
        line_length=options.get("line-length", 88),
        string_normalization=not options.get("skip-string-normalization", False),
        target_versions=target_versions,
    )
    include = re.compile(options.get("include", r"\.pyi?$"))
    exclude = re.compile(options.get("exclude", r"^$"))
    force_exclude = re.compile(options.get("force-exclude", r"^$"))
    return mode, include, exclude, force_exclude


def _source_files() -> list[Path]:
    _, include, exclude, force_exclude = _project_black_config()
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    candidates: list[Path] = []
    for entry in result.stdout.splitlines():
        path = PROJECT_ROOT / Path(entry)
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".pyi"}:
            continue
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        if not include.search(path.name):
            continue
        if exclude.search(relative) or force_exclude.search(relative):
            continue
        if any(part in PRUNED_DIRS for part in Path(relative).parts[:-1]):
            continue
        candidates.append(path)
    return sorted(candidates)


def main() -> int:
    mode, _, _, _ = _project_black_config()
    changed: list[str] = []
    failures: list[str] = []
    files = _source_files()
    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
            black.format_file_contents(source, fast=False, mode=mode)
        except black.NothingChanged:
            continue
        except (OSError, UnicodeDecodeError, black.InvalidInput) as exc:
            failures.append(f"{path.relative_to(PROJECT_ROOT).as_posix()}: {exc}")
        else:
            changed.append(path.relative_to(PROJECT_ROOT).as_posix())

    if failures:
        print("Black could not parse/read:")
        for failure in failures:
            print(f"  {failure}")
    if changed:
        print("Files need Black formatting:")
        for name in changed:
            print(f"  {name}")
    print(
        f"Black API check: {len(files)} files inspected, {len(changed)} need formatting, {len(failures)} errors"
    )
    return 1 if changed or failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
