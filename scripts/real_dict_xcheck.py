# -*- coding: utf-8 -*-
r"""真实字典 × 5 大脚本现状 交叉核查（纯离线，零网络）。

目的：用户澄清 script_data_dict.md 是「5 大脚本实际消费字段速查 / 改主字典发现错误后
快速定位脚本改动点」的索引。本脚本验证该索引是否滞后于 5 大脚本(+sc_datasource)当前代码：

  ① 真实字典里每个 push2 `fNN` 字段断言 → 当前代码是否真消费（字面量或 fields2 批量请求）
  ② 关键估值/语义字段 → 用现成采集数据（docs/field_verification/2026*/raw_push2_full.json、
     raw_ulist239.json）采样值离线背书，不联网
  ③ 腾讯 [NN] / ZHB Col[NN] → 用现成 raw_tencent.json / raw_zhb.json 离线核验存在性

基金流 f135-f149（含 ulist f62/f66/f72/f78/f84）已在 V17.0.16 单独订正，
本脚本仍报告其消费情况但**不**计入"新滞后"告警。

运行：python scripts/real_dict_xcheck.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REAL_DICT = ROOT / "docs" / "script_data_dict.md"
FV = ROOT / "docs" / "field_verification"
SCAN_DIRS = ["stock_common", "core", "scripts"]
SCAN_FILES = [
    "get_val_report.py", "get_mak_report.py", "get_sht_report.py",
    "get_med_report.py", "get_lng_report.py", "main.py",
]
EXCLUDE_DIR_NAMES = {"scratch", "__pycache__", ".tmp_audit", "tests", "scripts"}
SELF_EXCLUDE = {"scripts/real_dict_xcheck.py"}

# 基金流段（V17.0.16 已订正，不计入新滞后告警）
FUND_FLOW = {"f%d" % n for n in list(range(135, 150)) + [62, 66, 72, 78, 84]}

# 真实字典里"故意不消费"的否定语境关键词（命中则 NOT_CONSUMED 属预期、非滞后）
NEG_CTX = ["已剔除", "已从来源剔除", "删除", "不用", "停用", "~~", "证伪", "不再", "非主力", "名实不符"]

# 关键估值/语义字段 → 真实字典断言含义（仅用于离线采样报告，不自动判定对错）
KEY_SEMANTICS = {
    # 中文名统一依 §12.8.12e 规范中文名（通达信官方 1,924 表优先，同花顺/东财补齐）。
    # ⚠️ 2026-09-06 修正：原 f108/f109/f160 中文名**三者错位**——
    #    f108 误标"归母净利(年报)"、f109 误标"EPS(年报)"、f160 误标"扣非EPS(TTM)"，
    #    与字典已定案铁证（f108=扣非EPS TTM=65.1429、f109=归母净利年报=823.20亿、
    #    f160=年报EPS=65.8518）完全相反，按中文名取数时对撞必然全错。已按字典订正。
    "f162": "市盈率（动）", "f163": "市盈率（静）", "f167": "市净率",
    "f9": "市盈率（动）[ulist]", "f114": "市盈率（静）[ulist]", "f115": "市盈率（TTM）[ulist]",
    "f23": "市净率[ulist/clist]", "f182": "市场类型枚举（2/5/32/80）",
    "f198": "东财板块代码（BKxxxx）", "f50": "量比", "f178": "5日资金流数组",
    "f103": "经营现金流（TTM）", "f104": "营业收入（TTM）", "f105": "归母净利润（报告期）",
    "f108": "每股收益（扣非·TTM）", "f109": "归母净利润（年报）", "f160": "每股收益（年报）",
    "f190": "每股未分配利润", "f174": "52周最高价", "f175": "52周最低价",
}


def iter_py():
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
            yield p
    for name in SCAN_FILES:
        p = ROOT / name
        if p.exists():
            yield p


def scan_code_fnn():
    literal, batch = {}, {}
    for p in iter_py():
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(p.relative_to(ROOT))
        for m in re.finditer(r'["\'](f\d{1,4})["\']', text):
            literal.setdefault(m.group(1), set()).add(rel)
        for m in re.finditer(r'fields2["\']?\s*[:=]\s*["\']([f0-9,]+)["\']', text):
            for fld in m.group(1).split(","):
                fld = fld.strip()
                if re.fullmatch(r"f\d{1,4}", fld):
                    batch.setdefault(fld, set()).add(rel)
    return literal, batch


def _expand_range(a, b):
    lo, hi = int(a), int(b)
    if lo > hi or hi - lo > 500:
        return set()
    return {"f%d" % n for n in range(lo, hi + 1)}


def extract_real_dict_fnn():
    """返回 {fNN: set(line_no)}，含区间/斜杠展开。"""
    text = REAL_DICT.read_text(encoding="utf-8", errors="ignore")
    per_line = {}
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r"\bf(\d{1,4})\b", line):
            per_line.setdefault("f" + m.group(1), set()).add(i)
    # 区间简写 f135-146
    for m in re.finditer(r"\bf(\d{1,4})\s*[-–~]\s*f?(\d{1,4})\b", text):
        for f in _expand_range(m.group(1), m.group(2)):
            per_line.setdefault(f, set()).add(0)
    # 斜杠列举 f144/145/146
    for m in re.finditer(r"\bf(\d{1,4})((?:\s*/\s*\d{1,4})+)", text):
        base = "f" + m.group(1)
        per_line.setdefault(base, set()).add(0)
        for mm in re.finditer(r"\d{1,4}", m.group(2)):
            per_line.setdefault("f" + mm.group(0), set()).add(0)
    return per_line, text


def real_dict_lines_with_negation(text, lines):
    """lines: set(line_no)，0 表示区间展开无具体行。返回是否命中否定语境。"""
    if not lines or 0 in lines:
        # 区间展开：检查全文是否整体在否定章节（粗略）
        return False
    for ln in lines:
        if ln < 1 or ln > len(text.splitlines()):
            continue
        line = text.splitlines()[ln - 1]
        if any(k in line for k in NEG_CTX):
            return True
    return False


def latest_raw(sub):
    """返回 docs/field_verification 下最新一天的某 raw json 路径。"""
    days = sorted([p for p in (FV).iterdir() if p.is_dir()], reverse=True)
    for d in days:
        cand = d / sub
        if cand.exists():
            return cand
    return None


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def sample_push2_values(fields, n=5):
    """从最新 raw_push2_full.json 采样字段值（离线）。"""
    p = latest_raw("raw_push2_full.json")
    if not p:
        return None
    data = load_json(p)
    if not data:
        return None
    stocks = data.get("stocks", {})
    out = {f: [] for f in fields}
    cnt = {f: 0 for f in fields}
    for code, rec in stocks.items():
        dd = rec.get("data", {})
        if not isinstance(dd, dict):
            continue
        hit = False
        for f in fields:
            if f in dd:
                cnt[f] += 1
                if len(out[f]) < n:
                    out[f].append((code, dd[f]))
                hit = True
        if hit:
            pass
    return {"path": str(p), "samples": out, "present_counts": cnt,
            "total_stocks": len(stocks)}


def sample_ulist_values(fields, n=5):
    p = latest_raw("raw_ulist239.json")
    if not p:
        return None
    data = load_json(p)
    if not data:
        return None
    # ulist239 结构未知，尝试常见键
    out = {f: [] for f in fields}
    cnt = {f: 0 for f in fields}
    blob = None
    if isinstance(data, dict):
        # 常见：{"stocks":{...}} 或 {"data":[...]} 或 直接列表
        blob = data.get("stocks") or data.get("data") or data
    if isinstance(blob, dict):
        items = blob.values()
    elif isinstance(blob, list):
        items = blob
    else:
        items = []
    total = 0
    for rec in items:
        total += 1
        if not isinstance(rec, dict):
            continue
        dd = rec.get("data", rec)
        if not isinstance(dd, dict):
            continue
        for f in fields:
            if f in dd:
                cnt[f] += 1
                if len(out[f]) < n:
                    key = rec.get("code") or rec.get("secid") or "?"
                    out[f].append((key, dd[f]))
    return {"path": str(p), "samples": out, "present_counts": cnt, "total_items": total}


def main():
    literal, batch = scan_code_fnn()
    consumed = {}
    for k, v in literal.items():
        consumed.setdefault(k, {"lit": set(), "bat": set()})["lit"] |= v
    for k, v in batch.items():
        consumed.setdefault(k, {"lit": set(), "bat": set()})["bat"] |= v

    rd_lines, rd_text = extract_real_dict_fnn()

    # ① 真实字典 fNN 断言 × 代码消费
    print("=" * 82)
    print("真实字典(script_data_dict.md) fNN 字段 × 5 大脚本+sc_datasource 代码消费 交叉核查")
    print("=" * 82)
    print(f"真实字典提及 fNN 字段数 : {len(rd_lines)}")
    print(f"生产代码消费 fNN 字段数 : {len(consumed)}")
    print()

    lag = []          # 真实字典断言消费但代码未消费（非基金流、非否定语境）
    ok_consumed = []  # 一致
    neg_ok = []       # 故意不消费（否定语境）
    for f in sorted(rd_lines, key=lambda x: int(x[1:])):
        is_fund = f in FUND_FLOW
        c = consumed.get(f)
        if c:
            ok_consumed.append(f)
            continue
        # 代码未消费
        if real_dict_lines_with_negation(rd_text, rd_lines[f]):
            neg_ok.append(f)
        elif is_fund:
            pass  # 基金流已订正，跳过
        else:
            lag.append(f)

    print(f"✅ 一致（真实字典断言且代码消费）: {len(ok_consumed)} 个")
    print(f"🚫 故意不消费(否定语境, 预期)    : {len(neg_ok)} 个 -> {', '.join(sorted(neg_ok, key=lambda x:int(x[1:]))) or '无'}")
    print(f"⚠️  疑似滞后（真实字典断言消费, 代码未消费, 非基金流）: {len(lag)} 个")
    for f in sorted(lag, key=lambda x: int(x[1:])):
        lns = sorted(x for x in rd_lines[f] if x > 0)
        where = f" 行 {lns}" if lns else " (区间/列举展开)"
        print(f"   {f:<6}{where}")
    print()

    # ② 反向缺口：代码消费但真实字典未提（真实字典可能漏记）
    rev = sorted((k for k in consumed if k not in rd_lines), key=lambda x: int(x[1:]))
    print(f"🔍 反向缺口（代码消费, 真实字典零提及）: {len(rev)} 个")
    for f in rev:
        c = consumed[f]
        tag = "批量" if c["bat"] and not c["lit"] else "字面量"
        where = sorted(c["lit"] | c["bat"])[:2]
        print(f"   {f:<6} [{tag}] {', '.join(where)}")
    print()

    # ③ 关键语义字段离线采样（现成采集数据）
    print("-" * 82)
    print("关键估值/语义字段 离线采样（现成 raw_push2_full.json / raw_ulist239.json）")
    print("-" * 82)
    p2_fields = [f for f in KEY_SEMANTICS if f not in ("f9", "f114", "f115", "f23")]
    ul_fields = ["f9", "f114", "f115", "f23"]
    p2 = sample_push2_values(p2_fields)
    if p2:
        print(f"[push2_full] {p2['path']}  样本股 {p2['total_stocks']} 只")
        for f in p2_fields:
            cc = p2["present_counts"].get(f, 0)
            sm = p2["samples"].get(f, [])
            note = KEY_SEMANTICS[f]
            if cc == 0:
                print(f"   {f:<6} [{note}] ⚠️ 采集数据未含此字段(可能未请求)")
            else:
                vals = ", ".join(str(v) for _, v in sm[:3])
                print(f"   {f:<6} [{note}] 出现 {cc} 只, 样例: {vals}")
    else:
        print("   ⚠️ 未找到 raw_push2_full.json")
    print()
    ul = sample_ulist_values(ul_fields)
    if ul:
        print(f"[ulist239] {ul['path']}  条目 {ul['total_items']}")
        for f in ul_fields:
            cc = ul["present_counts"].get(f, 0)
            sm = ul["samples"].get(f, [])
            note = KEY_SEMANTICS[f]
            if cc == 0:
                print(f"   {f:<6} [{note}] ⚠️ 采集数据未含此字段")
            else:
                vals = ", ".join(str(v) for _, v in sm[:3])
                print(f"   {f:<6} [{note}] 出现 {cc} 条, 样例: {vals}")
    else:
        print("   ⚠️ 未找到 raw_ulist239.json")
    print()

    # ④ 腾讯 [NN] / ZHB Col[NN] 离线存在性（现成 raw_tencent.json / raw_zhb.json）
    print("-" * 82)
    print("腾讯 [NN] / ZHB Col[NN] 离线存在性（现成 raw_tencent.json / raw_zhb.json）")
    print("-" * 82)
    ten = load_json(latest_raw("raw_tencent.json"))
    zhb = load_json(latest_raw("raw_zhb.json"))
    # 提取真实字典里的 [NN] 与 Col[NN]
    ten_idx = set()
    zhb_col = set()
    for m in re.finditer(r"\[(\d{1,3})\]", rd_text):
        ten_idx.add(int(m.group(1)))
    for m in re.finditer(r"Col\[(\d{1,3})\]", rd_text):
        zhb_col.add(int(m.group(1)))
    # 探测 tencent 数据里是否有这些下标（取第一条记录的键集合）
    ten_keys = set()
    if isinstance(ten, dict):
        blob = ten.get("stocks") or ten.get("data") or ten
        if isinstance(blob, dict):
            first = next(iter(blob.values()), None)
            if isinstance(first, dict):
                ten_keys = set(first.keys())
        elif isinstance(blob, list) and blob:
            if isinstance(blob[0], dict):
                ten_keys = set(blob[0].keys())
    zhb_keys = set()
    if isinstance(zhb, dict):
        blob = zhb.get("stocks") or zhb.get("data") or zhb
        if isinstance(blob, dict):
            first = next(iter(blob.values()), None)
            if isinstance(first, dict):
                zhb_keys = set(first.keys())
        elif isinstance(blob, list) and blob:
            if isinstance(blob[0], dict):
                zhb_keys = set(blob[0].keys())
    print(f"真实字典腾讯 [NN] 提及: {sorted(ten_idx)}")
    if ten_keys:
        # tencent 字段键可能是字符串数字
        present = {i for i in ten_idx if (str(i) in ten_keys or f"[{i}]" in ten_keys or f"f{i}" in ten_keys)}
        print(f"  采集数据首条键样本(前15): {sorted(ten_keys)[:15]}")
        print(f"  命中存在: {sorted(present)}")
        miss = sorted(ten_idx - present)
        if miss:
            print(f"  ⚠️ 采集数据未直接含下标(可能键名不同, 需人工核对): {miss}")
    else:
        print("  ⚠️ 未找到 raw_tencent.json 或结构未知")
    print(f"真实字典 ZHB Col[NN] 提及: {sorted(zhb_col)}")
    if zhb_keys:
        present = {i for i in zhb_col if (str(i) in zhb_keys or f"col{i}" in zhb_keys or f"Col[{i}]" in zhb_keys)}
        print(f"  采集数据首条键样本(前20): {sorted(zhb_keys)[:20]}")
        print(f"  命中存在: {sorted(present)}")
        miss = sorted(zhb_col - present)
        if miss:
            print(f"  ⚠️ 采集数据未直接含 Col 下标(键名可能不同): {miss}")
    else:
        print("  ⚠️ 未找到 raw_zhb.json 或结构未知")


if __name__ == "__main__":
    main()
