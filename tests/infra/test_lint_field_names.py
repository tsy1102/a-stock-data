import importlib.util
from pathlib import Path
from typing import Callable

_script_path = Path(__file__).resolve().parents[2] / "scripts" / "lint_field_names.py"
_spec = importlib.util.spec_from_file_location("_lint_field_names", _script_path)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
_find_violations: Callable[[list[str]], list[tuple[int, str, str]]] = getattr(
    _module, "_find_violations"
)


def test_checks_only_canonical_field_name_column() -> None:
    lines = [
        "| 规范中文名 | 语义与口径 | 各源字段对照（均为别名） |",
        "|:---|:---|:---|",
        "| 现价 | 最新成交价 | push2 `f43` / 最新价 |",
        "| 昨收盘 | 前一交易日收盘价 | 新浪 `pre_close` / 昨收价 |",
        "",
        "正文中的原始标签：市盈率(TTM)、最新价、昨收价。",
        "| 原始字段 | 网站标签 |",
        "| `pe_ttm` | 市盈率(TTM) |",
    ]

    assert _find_violations(lines) == []


def test_reports_forbidden_aliases_and_half_width_pe_in_canonical_names() -> None:
    lines = [
        "| 规范中文名 | 语义与口径 | 各源字段对照 |",
        "|---|---|---|",
        "| 最新价 | 最新成交价 | push2 `f43` |",
        "| 市盈率(TTM) | 滚动市盈率 | fuyao `pe_ttm` |",
    ]

    violations = _find_violations(lines)

    assert [violation[1] for violation in violations] == [
        "禁用异名回归: 最新价",
        "PE 半角括号回归: 市盈率(TTM)",
    ]
