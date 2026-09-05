# -*- coding: utf-8 -*-
r"""字典字段落地核查 v3：字典 f 字段 × 生产代码消费 的全量比对。

版本演进（每次修正都是为了压掉误报，勿回退）：
  v1 误报来源：
    ① kline 类字段（f51-f61）通过 `fields2: "f51,...,f61"` 请求 + **位置索引** `_p[10]` 解析，
       代码中不存在 `"f61"` 字面量 → 被误判为"零消费"。
    ② 字典登记判定过窄（只抓四列表格行），f2/f162 等在字典其他章节有记录却被判为"未登记"。
  v2 修正：
    - 消费判定 = `"fNN"` 字面量 **或** 出现在 `fields2` 批量请求串中。
    - 登记判定 = 该 fNN 在 field_dict.md **全文**任何位置出现。
  v3 修正（2026-08-31，f145 暴露的盲区）：
    - v2 的登记判定只认 `\bf(\d{1,4})\b` 全字匹配，识别不了字典里大量存在的
      **区间简写**（`f135-146`）与**斜杠列举**（`f144/145/146`）。
      结果：f144/145/146 明明写了，却被判成"字典零提及"（假阴）。
    - v3 新增区间/列举展开，并**区分两种登记强度**：
        * `mentioned`   —— 有独立的 `fNN` 字面量（强登记，可精确定位）
        * `range_only`  —— 只出现在区间简写里（弱登记，**查不到专属说明**）
      「仅区间提及」单列为 ②b 类警示：它比「零提及」更隐蔽——
      阅读者会以为"字典里有"，但真要查 f145 是什么，全文检索定位不到任何一行。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT_PATH = ROOT / "docs" / "field_dict.md"

SCAN_DIRS = ["stock_common", "core", "scripts"]
SCAN_FILES = [
    "get_val_report.py", "get_mak_report.py", "get_sht_report.py",
    "get_med_report.py", "get_lng_report.py", "main.py",
]
EXCLUDE_DIR_NAMES = {"scratch", "__pycache__", ".tmp_audit", "tests"}
# 本脚本自身含 fNN 示例字符串，需排除，避免自我污染
SELF_EXCLUDE = {"scripts/field_landing_audit.py"}


def collect_prod_py_files():
    files = []
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            if any(part in EXCLUDE_DIR_NAMES for part in p.parts):
                continue
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            if rel in SELF_EXCLUDE:
                continue
            files.append(p)
    for name in SCAN_FILES:
        p = ROOT / name
        if p.exists():
            files.append(p)
    return files


def scan_code():
    """返回 ({field: set(文件)}, {field: set((文件, fields2串))})"""
    literal, batch = {}, {}
    for p in collect_prod_py_files():
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(p.relative_to(ROOT))
        for m in re.finditer(r'["\'](f\d{1,4})["\']', text):
            literal.setdefault(m.group(1), set()).add(rel)
        # fields2: "f51,f52,...,f61" 形式（允许单引号、无引号 key）
        for m in re.finditer(r'fields2["\']?\s*[:=]\s*["\']([f0-9,]+)["\']', text):
            for fld in m.group(1).split(","):
                fld = fld.strip()
                if re.fullmatch(r"f\d{1,4}", fld):
                    batch.setdefault(fld, set()).add(rel)
    return literal, batch


# 区间/列举展开的上限：防止 "f1-f9999" 之类误匹配炸出上万个字段
_MAX_RANGE_SPAN = 500


def _expand_range(a, b):
    """闭区间 [a,b] 展开为字段名集合；跨度过大则视为误匹配，返回空集。"""
    lo, hi = int(a), int(b)
    if lo > hi or hi - lo > _MAX_RANGE_SPAN:
        return set()
    return {"f%d" % n for n in range(lo, hi + 1)}


def _expand_slash_list(first, rest):
    """`f144/145/146` → {f144,f145,f146}。"""
    out = {"f" + first}
    for m in re.finditer(r"\d{1,4}", rest):
        out.add("f" + m.group(0))
    return out


def dict_mentioned():
    """扫描字典全文，返回 (counts, range_only, text)。

    counts     —— 每个字段作为**独立 `fNN` 字面量**出现的次数（强登记）
    range_only —— 只在区间简写/斜杠列举里出现的字段集合（弱登记）
    """
    if not DICT_PATH.exists():
        return {}, set(), ""
    text = DICT_PATH.read_text(encoding="utf-8", errors="ignore")
    counts = {}
    for m in re.finditer(r"\bf(\d{1,4})\b", text):
        counts["f" + m.group(1)] = counts.get("f" + m.group(1), 0) + 1

    # 区间简写：f135-146 / f135 - f146 / f135–f146 / f135~f146
    range_hits = set()
    for m in re.finditer(r"\bf(\d{1,4})\s*[-–~]\s*f?(\d{1,4})\b", text):
        range_hits |= _expand_range(m.group(1), m.group(2))
    # 斜杠列举：f144/145/146
    for m in re.finditer(r"\bf(\d{1,4})((?:\s*/\s*\d{1,4})+)", text):
        range_hits |= _expand_slash_list(m.group(1), m.group(2))

    range_only = range_hits - set(counts)
    return counts, range_only, text


def dict_verified_rows(text):
    """抓 `| fNN | 含义 | 单位 | 状态 |` 表格行，返回 {field: (含义, 状态)}"""
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*\*{0,2}(f\d{1,4})\*{0,2}\s*\|([^|]*)\|([^|]*)\|(.*)\|\s*$", line)
        if m:
            field, meaning, _unit, status = m.groups()
            rows.setdefault(field.strip(), (meaning.strip(), status.strip()))
    return rows


def is_verified(status):
    return "✅" in status and "❌" not in status and "已证伪" not in status


def _num(k):
    return int(k[1:])


def main():
    literal, batch = scan_code()
    mentioned, range_only, text = dict_mentioned()
    verified_rows = dict_verified_rows(text)

    consumed = {}
    for k, v in literal.items():
        consumed.setdefault(k, {"literal": set(), "batch": set()})["literal"] |= v
    for k, v in batch.items():
        consumed.setdefault(k, {"literal": set(), "batch": set()})["batch"] |= v

    verified_fields = {k for k, (_m, s) in verified_rows.items() if is_verified(s)}

    # ① 字典标为已核实，但代码既无字面量也不在 fields2 批量请求中
    gap_verified_not_used = sorted(
        k for k in verified_fields
        if k not in consumed
    )
    # ② 代码消费了，但字典全文都没提过 → 真正的文档滞后
    gap_used_not_documented = sorted(
        k for k in consumed if k not in mentioned and k not in range_only
    )
    # ②b 代码消费了，但字典只在区间简写里带过（f135-146 / f144/145/146），查无专属说明
    gap_range_only = sorted(
        k for k in consumed if k not in mentioned and k in range_only
    )
    # ③ 代码消费 + 字典提过但没有四列表格行（登记在其他章节）
    soft_documented = sorted(
        k for k in consumed if k in mentioned and k not in verified_rows
    )

    print("=" * 80)
    print("字典字段落地核查 v3（push2 f 字段）")
    print("=" * 80)
    print(f"字典全文出现过的 f 字段 : {len(mentioned)}  （另有 {len(range_only)} 个只在区间简写里出现）")
    print(f"字典有四列表格行        : {len(verified_rows)}")
    print(f"  其中判定「已核实」    : {len(verified_fields)}")
    print(f"生产代码消费（字面量∪批量）: {len(consumed)}")
    print(f"  其中走 fields2 位置索引 : {len(batch)}")
    print()

    print(f"⚠️  ① 字典已核实 + 代码零消费 : {len(gap_verified_not_used)}")
    print(f"📌 ② 代码消费 + 字典零提及   : {len(gap_used_not_documented)}  （真·文档滞后）")
    print(f"📎 ②b 代码消费 + 仅区间简写登记 : {len(gap_range_only)}  （比零提及更隐蔽，应补专属行）")
    print(f"   ③ 代码消费 + 字典有提及但无表格行 : {len(soft_documented)}  （记录在别章节，可接受）")
    print()

    if gap_verified_not_used:
        print("-" * 80)
        print("⚠️  ①【字典标为已核实，但生产代码零消费】—— 需逐条甄别")
        print("-" * 80)
        for k in sorted(gap_verified_not_used, key=_num):
            meaning, status = verified_rows[k]
            print(f"  {k:<6} {meaning[:30]:<32} 字典提及 {mentioned.get(k,0):>3} 次")
        print()

    if gap_used_not_documented:
        print("-" * 80)
        print("📌 ②【代码消费，但 field_dict.md 全文零提及】—— 文档滞后，应补登记")
        print("-" * 80)
        for k in sorted(gap_used_not_documented, key=_num):
            src = consumed[k]
            where = sorted(src["literal"] | src["batch"])[:2]
            tag = "批量" if src["batch"] and not src["literal"] else "字面量"
            print(f"  {k:<6} [{tag}] {', '.join(where)}")
        print()

    if gap_range_only:
        print("-" * 80)
        print("📎 ②b【代码消费，但字典只在区间简写里带过，查无专属说明】—— 应补逐号表")
        print("-" * 80)
        for k in sorted(gap_range_only, key=_num):
            src = consumed[k]
            where = sorted(src["literal"] | src["batch"])[:2]
            tag = "批量" if src["batch"] and not src["literal"] else "字面量"
            print(f"  {k:<6} [{tag}] {', '.join(where)}")
        print()

    if soft_documented:
        print("-" * 80)
        print("   ③【代码消费 + 字典有提及但无专属表格行】—— 登记在别章节")
        print("-" * 80)
        for k in sorted(soft_documented, key=_num):
            print(f"  {k:<6} 字典提及 {mentioned.get(k,0):>3} 次")
        print()


if __name__ == "__main__":
    main()
