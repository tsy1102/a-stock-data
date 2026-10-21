from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def load_state(state_path: str | Path) -> dict[str, Any]:
    if os.path.exists(state_path):
        try:
            with open(state_path, encoding="utf-8") as handle:
                state = json.load(handle)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            return {
                "version": 2,
                "findings": {},
                "warnings": [f"state 读取失败，未覆盖原文件: {exc}"],
                "read_error": True,
            }
        if not isinstance(state, dict):
            return {
                "version": 2,
                "findings": {},
                "warnings": ["state 顶层不是对象，未覆盖原文件"],
                "read_error": True,
            }
        if not isinstance(state.get("findings", {}), dict):
            return {
                "version": 2,
                "findings": {},
                "warnings": ["state.findings 格式无效，未覆盖原文件"],
                "read_error": True,
            }
        version = state.get("version", 1)
        if not isinstance(version, int) or version > 2:
            return {
                "version": 2,
                "findings": {},
                "warnings": [f"collision_state 版本 {version!r} 不受支持，未覆盖原文件"],
                "read_error": True,
            }
        if version < 2:
            old_findings = state.get("findings", {})
            migrated = {
                "version": 2,
                "findings": {},
                "legacy_findings_v1": old_findings,
                "legacy_state_version": version,
                "warnings": [
                    f"collision_state v{version} 已归档到 legacy_findings_v1；旧 L1 不再自动视为当前确认"
                ],
            }
            return migrated
        state.setdefault("findings", {})
        state.setdefault("warnings", [])
        return state
    return {"version": 2, "findings": {}, "warnings": []}


def save_state(state_path: str | Path, st: dict[str, Any]) -> None:
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
