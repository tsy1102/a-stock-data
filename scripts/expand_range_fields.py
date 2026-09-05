# -*- coding: utf-8 -*-
r"""将两个字典中的「区间串/斜杠列举」字段记录方式，按其他字段的方式重排为单个 fNN 记号。

规则（依据用户对「仅拆语义字段组 + 内联单号记号」的确认）：
  1. 区间串 fA[-–~]fB（A<=2 且 B>=100）→ 视为「请求域通配」（一次返回全部字段），
     保留原写法并追注 (请求域通配)，不展开。
  2. 其余区间串 → 展开为内联单号记号 fA/f(A+1)/.../fB。
  3. 斜杠列举中"缺 f 前缀"的记号（如 f62/64/65/66）→ 归一为 f62/f64/f65/f66。
     已全带 f 前缀的斜杠列举（如 f103/f105/f109）保持不变。

纯离线、只读+写回两个字典文件。运行后请用 grep 复核无非通配区间串残留。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [ROOT / "docs" / "field_dict.md", ROOT / "docs" / "script_data_dict.md"]

RANGE = re.compile(r"f(\d{1,4})\s*[-–~]\s*f?(\d{1,4})")
SLASH = re.compile(r"f(\d{1,4})((?:/\d{1,4})+)")

WILDCARD_SEP = {"~": "~", "-": "-", "–": "–"}  # 仅记录，展开用 /


def is_wildcard(lo, hi):
    return lo <= 2 and hi >= 100


def expand_ranges(text):
    out = []
    pos = 0
    for m in RANGE.finditer(text):
        lo, hi = int(m.group(1)), int(m.group(2))
        out.append(text[pos:m.start()])
        if is_wildcard(lo, hi):
            sep = m.group(0)[m.group(0).find("f", 1):][0] if False else None
            # 还原原分隔符
            sep_ch = "-" 
            for ch in ("~", "–", "-"):
                if ch in m.group(0):
                    sep_ch = ch
                    break
            out.append(f"f{lo}{sep_ch}f{hi}(请求域通配)")
            out.append(f"  [KEEP 通配 f{lo}{sep_ch}f{hi}]")
        else:
            toks = "/".join(f"f{n}" for n in range(lo, hi + 1))
            out.append(toks)
            out.append(f"  [EXPAND f{lo}-{hi} -> {toks}]")
        pos = m.end()
    out.append(text[pos:])
    # 去掉调试标注行（避免污染字典正文）
    new_text = "".join(seg for seg in out if not seg.startswith("  ["))
    debug = [seg for seg in out if seg.startswith("  [")]
    return new_text, debug


def normalize_slash(text):
    debug = []

    def repl(m):
        first = m.group(1)
        rest = m.group(2)  # e.g. "/64/65/66" or "/f136/..." (后者不会被本正则匹配)
        parts = []
        changed = False
        for tok in rest.lstrip("/").split("/"):
            if not tok:
                continue
            parts.append(f"f{tok}")
            if not tok.startswith("f"):
                changed = True
        result = f"f{first}/" + "/".join(parts)
        if changed:
            debug.append(f"  [SLASH {m.group(0)} -> {result}]")
        return result

    return SLASH.sub(repl, text), debug


def main():
    for f in FILES:
        text = f.read_text(encoding="utf-8")
        new, d1 = expand_ranges(text)
        new, d2 = normalize_slash(new)
        if new != text:
            f.write_text(new, encoding="utf-8")
        print(f"===== {f.name} =====")
        print(f"  区间串处理: {len(d1)} 处")
        for x in d1:
            print(x)
        print(f"  斜杠归一: {len(d2)} 处")
        for x in d2:
            print(x)
        print()


if __name__ == "__main__":
    main()
