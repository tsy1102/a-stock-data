# -*- coding: utf-8 -*-
"""补充核查：P1 黄色 21 token 在保留区是否有权威定义/注册表行（排除 false negative）。"""
import re

P = "docs/field_dict.md"
lines = open(P, encoding="utf-8").read().split("\n")
MOVE = [(947, 1152), (1153, 1203), (4398, 5540)]
def in_range(i):
    return any(a <= i <= b for a, b in MOVE)
keep_lines = [l for i, l in enumerate(lines, 1) if not in_range(i)]
keep_text = "\n".join(keep_lines)

# 注册表区域：从 "#### 12.8.12e 规范字段注册表" 起到下一个 "####" 或 "## §13"
start = next(i for i, l in enumerate(keep_lines) if "12.8.12e 规范字段注册表" in l)
reg_lines = []
for l in keep_lines[start:]:
    if l.startswith("## §13") or (l.startswith("####") and "12.8.12e" not in l and "规范字段注册表" not in l):
        break
    reg_lines.append(l)
reg_text = "\n".join(reg_lines)
print(f"注册表区域行数: {len(reg_lines)} (起始 keep 行 ~{start+1})")

# 21 个黄色 token（来自 dry-run 报告）
toks = ["103","109","116","117","136","138","139","144","145","146","149",
        "160","163","164","165","166","167","168","170","171","190","199"]
# 去重（保证唯一）
toks = sorted(set(toks), key=lambda x:int(x))

def has_def_row(t):
    # 表格首列定义行： | f{t} |  或  | [t] |（含 f 前缀）
    pat = re.compile(r'\|\s*f?\[?' + re.escape(t) + r'\]?\s*\|')
    in_keep = bool(pat.search(keep_text))
    in_reg = bool(pat.search(reg_text))
    return in_keep, in_reg

print(f"\n{'token':<6} {'keep定义行':<12} {'注册表行':<10}")
uncertain = []
for t in toks:
    ik, ir = has_def_row(t)
    flag = "OK" if (ik or ir) else "!!缺失"
    if not (ik or ir):
        uncertain.append(t)
    print(f"  {t:<5} {str(ik):<12} {str(ir):<10} {flag}")

print(f"\n在保留区有定义行/注册表行的 token: {len(toks)-len(uncertain)}/{len(toks)}")
print(f"仍缺失（须 port）: {uncertain if uncertain else '无'}")
