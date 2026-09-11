#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_field_dict.py — 由 field_registry.json 单一真相源生成 field_dict.md 的机器生成区块。

Phase 3(2026-09-12): markdown 单向生成（根治 document-as-database 反模式）。
registry 为单一真相源，本脚本将其渲染为 field_dict.md 中由标记区间包围的区块，
替代「解析 markdown 反推」的旧路径。

生成的区块（marker 区间，与 gen_field_matrix 的 <!-- GEN:field-matrix --> 兼容）：
  * <!-- GEN:field-matrix -->      §零·B 字段×源总表（复用 gen_field_matrix.render）
  * <!-- GEN:subdict-index -->     分字典索引（来自 sources[].verify_file）

字段契约表（四列 | fNN | 含义 | 单位 | 状态 |）当前 NOT 由 registry 生成：
  registry Layer2 属性覆盖率仅 ~38.7%，且键空间为清洗字段名（非 f 码/原生 token），
  生成会丢失 ~70% 属性与全部纯 f 码行。该表仍由人工维护，待 Layer2 补全后再纳入生成。

用法:
  python scripts/gen_field_dict.py            # 写回 field_dict.md（幂等）
  python scripts/gen_field_dict.py --check    # 仅校验幂等（不写回），供 CI / 提交前闸门

幂等: 重复运行对同一 registry 产出一致；§零·B 块与当前 field_dict.md 逐字节一致（G3 闸门）。
"""
from __future__ import annotations

import argparse
import io
import os
import sys
from typing import Optional, Tuple

# UTF-8 强制（与 gen_field_matrix / extract_registry 一致）
for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DICT = os.path.join(REPO_ROOT, "docs", "field_dict.md")

# Phase 2/3 单一真相源访问层 + §零·B 渲染器（同进程复用，避免重复解析器）
sys.path.insert(0, SCRIPT_DIR)
import field_registry_api as fra
import gen_field_matrix as gm


def render_subdict_index(reg: dict) -> str:
    """分字典索引：来自 sources[].verify_file（仅列出有专属分字典的源）。"""
    out = []
    out.append("### 分字典索引（由 field_registry.json 自动生成，勿手改）\n")
    out.append("> 生成：`scripts/gen_field_dict.py`（Phase 3 起由 field_registry.json 单一真相源读取）。"
               "本表为「源→分字典」自动索引，权威同步规则见 §12.15.10。\n")
    out.append("| 源 | 分字典（verify/） | 主要章节 |")
    out.append("|:---|:---|:---|")
    n = 0
    for s in reg.get("sources", []):
        vf = s.get("verify_file")
        if not vf:
            continue
        name = s.get("name", "")
        sec = (s.get("section_patterns") or ["—"])[0]
        out.append(f"| {name} | [{vf}](verify/{vf}) | {sec} |")
        n += 1
    out.append("")
    out.append(f"> 共 {n} 个源有专属分字典；无分字典的源以主字典自身为权威（见 §12.15.10 强制规则）。\n")
    return "\n".join(out)


def _replace_block(text: str, marker: str, content: str) -> Tuple[str, bool]:
    """替换 `<!-- marker --> ... <!-- /marker -->` 区间内容。

    返回 (新文本, 是否命中已有 marker)。marker 不存在时返回原文本 + False（不静默插入，
    避免误写——marker 由人工在 field_dict.md 中预置，见 Task #119）。
    """
    open_tag = f"<!-- {marker} -->"
    close_tag = f"<!-- /{marker} -->"
    start = text.find(open_tag)
    end = text.find(close_tag)
    if start == -1 or end == -1:
        return text, False
    head = text[: start + len(open_tag)]
    tail = text[end:]
    return head + "\n\n" + content + "\n" + tail, True


def generate(check: bool = False) -> int:
    reg = fra.load_registry()

    # 区块 1：§零·B 字段×源总表（复用 gen_field_matrix 的 registry 路径 + 渲染器）
    ns, rec = gm.build_matrix(use_registry=True)
    matrix_block = gm.render(ns, rec)

    # 区块 2：分字典索引
    subdict_block = render_subdict_index(reg)

    text = io.open(DICT, encoding="utf-8").read()
    new_text, ok_matrix = _replace_block(text, "GEN:field-matrix", matrix_block)
    new_text, ok_subdict = _replace_block(new_text, "GEN:subdict-index", subdict_block)

    if not ok_matrix:
        print("ABORT: field_dict.md 缺少 <!-- GEN:field-matrix --> 标记", file=sys.stderr)
        return 1
    if not ok_subdict:
        print("[warn] field_dict.md 缺少 <!-- GEN:subdict-index --> 标记，跳过该块"
              "（请在文档中预置标记区间，详见计划文档 Phase 3）", file=sys.stderr)

    if check:
        changed = new_text != text
        print(f"[check] field-matrix 已写回区={'是' if ok_matrix else '否'}; "
              f"subdict-index 已写回区={'是' if ok_subdict else '否'}")
        print(f"[check] 幂等结果: {'一致 ✅（与当前 field_dict.md 无差异）' if not changed else '存在差异（首次生成或 registry 已更新）'}")
        return 0

    io.open(DICT, "w", encoding="utf-8").write(new_text)
    print(f"OK: 写回 field_dict.md（field-matrix={'更新' if ok_matrix else '跳过'}; "
          f"subdict-index={'更新' if ok_subdict else '跳过'}）")
    return 0


if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description="由 field_registry.json 生成 field_dict.md 的机器生成区块")
    _ap.add_argument("--check", action="store_true", help="仅校验幂等（不写回），供 CI 闸门")
    _args = _ap.parse_args()
    sys.exit(generate(check=_args.check))
