"""Compile Git-visible Python sources into the ignored project temp directory."""

from __future__ import annotations

import py_compile
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / ".tmp" / "py_compile_all"


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    sources: list[Path] = []
    for entry in result.stdout.splitlines():
        if not entry.endswith(".py"):
            continue
        source = PROJECT_ROOT / Path(entry)
        if source.is_file():
            sources.append(source)
    sources.sort()
    failures: list[str] = []
    for source in sources:
        relative = source.relative_to(PROJECT_ROOT)
        target = OUTPUT_ROOT / relative.with_suffix(".pyc")
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            py_compile.compile(str(source), cfile=str(target), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"{relative.as_posix()}: {exc.msg}")
    if failures:
        print("Python syntax failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print(f"Python syntax check: PASS ({len(sources)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
