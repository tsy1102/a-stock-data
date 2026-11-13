"""Stable hashes for textual evidence files across Git newline conversions."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def canonical_text_file_sha256(path: str | Path) -> str:
    """Hash a text file after converting all line endings to canonical LF."""
    content = Path(path).read_bytes()
    lf_content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(lf_content).hexdigest()


def text_file_sha256_candidates(path: str | Path) -> frozenset[str]:
    """Return hashes for the file's bytes and its LF/CRLF text representations.

    Git attributes may normalize a text evidence file between LF and CRLF when it
    enters or leaves the index. Newline-only changes do not alter the evidence's
    text, so readers accept either canonical line-ending representation while
    still requiring every other byte to match.
    """
    content = Path(path).read_bytes()
    lf_content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    crlf_content = lf_content.replace(b"\n", b"\r\n")
    return frozenset(
        hashlib.sha256(candidate).hexdigest() for candidate in (content, lf_content, crlf_content)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="计算文本证据文件的规范 LF SHA-256")
    parser.add_argument("path", type=Path, help="证据文本或其他文本文件路径")
    args = parser.parse_args()
    print(canonical_text_file_sha256(args.path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
