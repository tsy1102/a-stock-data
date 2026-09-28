# -*- coding: utf-8 -*-
"""
字段名样式回归守卫（对应 §12.8.12e 铁律一/四/五）。

只盯两类会直接破坏对撞/命名的回归，避免对描述性半角括号（如 ×1(股)、净利润(元)）
的误伤：
  1) 禁用异名回归：核心旧别名（当前价/最新价/今开/昨收/封板资金/封单资金/52周高/52周低）
     不得再作为字段名出现（规范表/铁律区/代码围栏/接口契约原文除外）。
  2) PE 半角括号回归：全文字段名不得出现 市盈率(动)/(静)/(TTM) 半角写法
     （规范表已统一全角 市盈率（动/静/TTM），见铁律五）。

用法：python scripts/lint_field_names.py
退出码 1 = 发现违规（可作 CI/提交前检查）。
"""

import io, sys, os

# Phase 2(2026-09-12): 改用 ROOT 绝对路径，消除 CWD 耦合（G0 已标记：原相对路径在 CI 错误 CWD 下直接失败）。
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "docs", "field_dict.md")

# Only canonical names are normalized; raw source labels and prose must remain verbatim.
FORBID = {"当前价", "最新价", "今开价", "昨收价", "封板资金", "封单资金", "52周高", "52周低"}
PE_HALF_WIDTH_FORBIDDEN = ("市盈率(动)", "市盈率(静)", "市盈率(TTM)")


def _find_violations(lines: list[str]) -> list[tuple[int, str, str]]:
    in_field_table = False
    in_fence = False
    violations: list[tuple[int, str, str]] = []

    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip("\r\n")
        if "```" in line:
            in_fence = not in_fence
            in_field_table = False
            continue
        if in_fence:
            continue
        if not line.strip().startswith("|"):
            in_field_table = False
            continue

        cells = [cell.strip() for cell in line.split("|")]
        field_name = cells[1].strip("`*_ ") if len(cells) > 1 else ""
        if field_name == "规范中文名":
            in_field_table = True
            continue
        if not in_field_table or not field_name:
            continue
        if all(char in ":- " for char in field_name):
            continue

        if field_name in FORBID:
            violations.append((index + 1, "禁用异名回归: %s" % field_name, line.strip()[:80]))
        for pattern in PE_HALF_WIDTH_FORBIDDEN:
            if pattern in field_name:
                violations.append((index + 1, "PE 半角括号回归: %s" % pattern, line.strip()[:80]))
                break

    return violations


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    with io.open(PATH, encoding="utf-8") as field_file:
        violations = _find_violations(field_file.readlines())

    if violations:
        print("❌ 字段名样式检查失败，发现 %d 处违规：" % len(violations))
        for line_number, reason, text in violations[:60]:
            print("   行%d  %s  | %s" % (line_number, reason, text))
        return 1

    print("✅ 字段名样式检查通过：规范名列无禁用异名或 PE 半角括号。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
