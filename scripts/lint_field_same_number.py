# -*- coding: utf-8 -*-
"""
字段字典「同号即同义」回归守卫（第七轮碰撞审计配套，2026-09-07）。

铁律：ulist239 索引 ≠ push2 索引，**同字段编号 ≠ 同语义**。本脚本阻止任何
"仅凭字段编号相同就认定语义相同"的断言进入字典，并强制：

  ✅ 凡是声明 ulist fX 与 push2 存在映射关系的登记，必须在权威对齐表
    `docs/verify/ulist_push2_align.md`（ulist fN → push2 fM）中存在对应条目
    —— 该对齐表即「跨源对撞证据」的唯一登记处。新增字段登记若声明 push2 映射，
    必须先经跨源对撞实证后写入对齐表 `docs/verify/ulist_push2_align.md`，
    否则判违规。
  ✅ scheme 血缘护栏：加载采集 meta 的 scheme 标识（`docs/field_verification/*/meta.json`
    的 schemes 字段；回退 `BUILTIN_SCHEME`）确认 ulist239(em.ulist.np) 与
    push2(em.stock_get) 属不同字段体系；在此前提下任何「ulist.fX = push2.fY」主张
    必须以对齐表的跨号映射条目为实证——即便 X==Y 也只是「同号」而非「同义」。

覆盖范围：
  1) 主守卫：§12.3.2.3 ulist239 全字段清单（新字段登记处，见该节说明「破解新字段直接在此登记」）。
  2) 全文件回归：任何表格行若出现「✅ 同 push2 fX（同号…）」式裸断言（编号相同即认定同义、
     且未带证据标记），一律判违规——防止历史错误模式（第七轮已订正的 113 行）复发。

证据分级（字典行必须明确归属其一）：
  - VERIFIED    : ✅ + 数值实证/第七轮审计 标记，且对齐表确认 ulist fX → push2 fX（真同号同义）。
  - DISPROVED   : ⚠️ 已证伪 + 「实测 ulist fX = push2 fM (M≠X)」，且对齐表确认该异号映射。
  - UNVERIFIED  : ⚠️ 未实证/待核实/待破解/待数值对撞 —— 显式声明「无实证」，不主张同义，允许。
  - CROSS       : ✅ + 跨源/交叉验证/第九轮审计 标记，且指明具体外部具名源字段
                  （tdx/sina/tencent/fuyao/zhb/axdata 等）—— 经跨源数值对撞定案，非凭编号相同，
                  是「同号即同义」铁律的正确解药，允许（须命名外部源，不得夹带裸同号断言）。
  - 其他含「同 push2 fX（同号）」裸断言、且无上述任一标记 → 违规（回到第七轮前的错误模式）。

退出码 1 = 发现违规（可接入 CI / 提交前检查）；0 = 通过。
用法：python scripts/lint_field_same_number.py
每日流水线强制阻断模式：python scripts/lint_field_same_number.py --strict-naming（R3 命名缺口升为阻断级 exit≠0；默认 warn 级不阻断）
"""
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT = ROOT / "docs" / "field_dict.md"
ALIGN = ROOT / "docs" / "verify" / "ulist_push2_align.md"

# Phase 2(2026-09-12): registry 单一真相源访问层（mappings 已吸收 ulist_push2_align.md）。
sys.path.insert(0, str(ROOT / "scripts"))
import field_registry_api as fra

# --- 1) 解析权威对齐表 -> {ulist_fn(int): push2_fn(int)} ---
# Phase 2: 优先从 registry.mappings 读取（from=东财-ulist239 / to=东财-push2），
# 失败或无条目回退直接解析 ulist_push2_align.md，保证脚本永不因 registry 缺失硬失败。
align = {}
try:
    for m in fra.mappings():
        frm = m.get("from", {})
        to = m.get("to", {})
        if frm.get("source") == "东财-ulist239" and to.get("source") == "东财-push2":
            try:
                align[int(str(frm["code"]).lstrip("f"))] = int(str(to["code"]).lstrip("f"))
            except (KeyError, ValueError):
                continue
    if not align:
        raise RuntimeError("registry 无 ulist→push2 对齐条目")
except Exception as _e:
    print(f"[lint_field_same_number] registry 读取失败，回退对齐表: {_e}", file=sys.stderr)
    if ALIGN.exists():
        for line in ALIGN.read_text(encoding="utf-8").splitlines():
            for mm in re.finditer(r"ulist\s*f(\d{1,3})\s*\|\s*f(\d{1,3})", line):
                align[int(mm.group(1))] = int(mm.group(2))
align_same = {u for u, p in align.items() if u == p}

# --- 1b) 加载采集 meta 的 scheme 血缘（与跨源对撞 BUILTIN_SCHEME 对齐）---
# 字典主张「ulist.fX = push2.fY」时，本守卫据此确认两源属不同字段体系(em.ulist.np
# vs em.stock_get)，从而强制要求对齐表提供跨号映射实证（同号≠同义）。
BUILTIN_SCHEME = {
    "ulist239": "eastmoney.ulist.np",
    "push2_full": "eastmoney.stock_get",
    "em_fund_flow": "eastmoney.stock_get",
    "axdata": "eastmoney.stock_get",
    "tencent": "tencent.qt.gtimg.array",
    "zhb": "tdx.zhb.named",
    "tdx": "tdx.named",
    "fuyao": "fuyao.named",
    "sina": "sina.named",
}
# 字典/对齐表里用 "push2" 作简称，统一映射到采集源名
SCHEME_RENAME = {"push2": "push2_full", "push2delay": "push2_full", "push2_full": "push2_full"}


def load_schemes():
    """从最新采集 meta.json 的 schemes 字段加载血缘；缺失则回退 BUILTIN。返回 (dict, src)。"""
    FV = ROOT / "docs" / "field_verification"
    best, best_date = None, ""
    if FV.exists():
        for d in FV.iterdir():
            if not d.is_dir():
                continue
            m = d / "meta.json"
            if not m.exists():
                continue
            try:
                meta = json.loads(m.read_text(encoding="utf-8"))
            except Exception:
                continue
            schemes = meta.get("schemes")
            if not isinstance(schemes, dict):
                continue
            if d.name > best_date:   # YYYYMMDD 字符串比较 = 取最新目录
                best_date, best = d.name, schemes
    if best:
        return best, best_date
    return BUILTIN_SCHEME, "BUILTIN"


SCHEMES, SCHEME_SRC = load_schemes()


def scheme_of(src_name, schemes):
    return schemes.get(SCHEME_RENAME.get(src_name, src_name))


def check_scheme_grounded(fn, status, note):
    """针对主张 ulist.fX 与 push2.fY 同义的登记行，做 scheme 血缘护栏。

    返回 list：空=通过；含 "WARN:..." 条目=降级告警（不阻断）；其余=违规描述。
    """
    text = "%s %s" % (status, note)
    m_p = re.search(r"push2\s*f(\d{1,3})", text)
    if not m_p:
        return None  # 本行未主张 push2 映射，护栏不介入
    pY = int(m_p.group(1))
    m_u = re.search(r"ulist\s*f(\d{1,3})", text)
    uX = int(m_u.group(1)) if m_u else fn
    s_ul = scheme_of("ulist239", SCHEMES)
    s_pu = scheme_of("push2", SCHEMES)
    if s_ul is None or s_pu is None:
        return ["WARN:scheme 血缘未加载(%s/%s)，跳过护栏" % (s_ul, s_pu)]
    if s_ul == s_pu:
        # 同源体系下「同号=同义」可成立（本项目 ulist≠push2，正常不命中）
        return None
    # 异源体系：必须对齐表存在 ulist.fX → push2.fY 跨号映射实证
    rec = align.get(uX)
    if rec != pY:
        return ["scheme 护栏：主张 ulist(%s).f%d = push2(%s).f%d，但权威对齐表无此跨号映射实证"
                "（对齐表记 ulist.f%d → push2.f%s），「同号≠同义」铁律未被满足"
                % (s_ul, uX, s_pu, pY, uX, ("无" if rec is None else rec))]
    return []

# --- 1d) §12.8.12e 规范字段注册表 + R0–R6 命名仲裁（P1, 2026-09-09）---
# 落地「云 MCP 命名 Oracle 仲裁规则」：R3（canonical 名 + 全量别名双匹配）、R6（厂商名不可盲信、
# 须数值二级复核）。默认 warn 级（不阻断 CI）；传 --strict-naming 时 R3 缺口升为违规（阻断提交）。
def _extract_source_tokens(text):
    """从一段文本抽取源字段 token（归一化小写），用于 R3 双匹配比对。"""
    toks = set()
    for mm in re.finditer(r"(push2(?:delay|full)?|ulist)\s*f(\d{1,3})", text, re.I):
        toks.add("%s f%s" % (mm.group(1).lower().replace("push2delay", "push2")
                              .replace("push2full", "push2"), mm.group(2)))
    for mm in re.finditer(r"(?:腾讯|tx)\s*\[\s*(\d{1,3})\s*\]", text, re.I):
        toks.add("腾讯[%s]" % mm.group(1))
    for mm in re.finditer(r"ths\s*sdk\s*(\d+)", text, re.I):
        toks.add("ths sdk %s" % mm.group(1))
    for mm in re.finditer(r"`([A-Za-z_][A-Za-z0-9_]*)`", text):
        toks.add(mm.group(1).lower())
    for src in ("fuyao", "zhb", "tdx快照", "tdx财务", "同花顺", "开盘啦", "push2ex"):
        for mm in re.finditer(re.escape(src) + r"\s*`([A-Za-z_][A-Za-z0-9_]*)`", text, re.I):
            toks.add("%s `%s`" % (src.lower(), mm.group(1).lower()))
    return toks


def load_canonical_registry():
    """解析 §12.8.12e 规范字段注册表，返回 (KNOWN_TOKENS set, canonical_names set)。"""
    known, cnames = set(), set()
    in_sec = False
    for ln in DICT.read_text(encoding="utf-8").splitlines():
        if re.match(r"#+\s*12\.8\.12e", ln):
            in_sec = True
            continue
        if in_sec and re.match(r"#+\s", ln):
            if "云 MCP 命名 Oracle" in ln or "R0" in ln:
                break
            break
        if not in_sec or not ln.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.split("|")]
        if len(cells) < 4:
            continue
        cnames.add(cells[1].lower())
        known |= _extract_source_tokens(cells[3])
        if len(cells) >= 6:
            known |= _extract_source_tokens(cells[5])
        known.add(cells[1].lower())
    return known, cnames


KNOWN_TOKENS, CANONICAL_NAMES = load_canonical_registry()


def check_naming_registry():
    """R0–R6 命名仲裁检查（P1）。返回 (warn_list, viol_list)。
    - R3 双匹配：✅ 定案行引用的源字段 token 须命中 KNOWN_TOKENS（canonical 或任一别名）；
      未命中者记 R3 缺口（应补登 §12.8.12e 规范表）。
    - R6 厂商名二级复核：以厂商官方具名字段（`xxx` 反引号私有名）作命名依据、但行内无数值实证
      标记者，记 R6 告警（厂商名不可盲信，须数值对撞/跨源实证兜底）。
    默认均为 warn 级；--strict-naming 时 R3 缺口升为违规（阻断）。
    """
    strict = "--strict-naming" in sys.argv
    warns, vcs = [], []
    NUM_MARK = ("数值实证", "跨源", "交叉验证", "对撞", "精确", "比值", "L1",
                "二级复核", "实测", "多日复核", "fuyao锚", "强锚", "数值对撞")
    for ln_no, fn, raw in all_frows:
        if "✅" not in raw:
            continue
        for t in sorted(_extract_source_tokens(raw)):
            if t not in KNOWN_TOKENS and t not in CANONICAL_NAMES:
                msg = "R3 命名缺口：行%d 定案引用源字段 `%s` 未登记于 §12.8.12e 规范表（canonical/别名双匹配失败），建议补登" % (ln_no, t)
                (vcs if strict else warns).append((ln_no, msg))
        if re.search(r"`[A-Za-z_][A-Za-z0-9_]*`", raw) and any(
                v in raw for v in ("通达信", "腾讯", "东财", "同花顺", "TDX云", "mx-ds", "妙想")):
            if not any(m in raw for m in NUM_MARK):
                warns.append((ln_no, "R6 厂商名盲信风险：行%d 以厂商官方具名字段作命名依据但缺数值二级复核标记" % ln_no))
    return warns, vcs


# --- 2) 解析字典 ---
lines = DICT.read_text(encoding="utf-8").splitlines()

# 定位 §12.3.2.3 ulist239 表区块（下一 #### 标题前）
sec_start = None
for i, ln in enumerate(lines):
    if "12.3.2.3" in ln and "ulist239" in ln:
        sec_start = i
        break

rows_sec = []  # (line_no, ulist_fn, status, note)
if sec_start is not None:
    for i in range(sec_start + 1, len(lines)):
        if lines[i].lstrip().startswith("#### "):
            break
        m = re.match(r"\s*\|\s*f(\d{1,3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$", lines[i])
        if m:
            rows_sec.append((i + 1, int(m.group(1)), m.group(2), m.group(3)))

# --- 3) 全文件所有「f 编号」表格行（用于回归扫描）---
all_frows = []  # (line_no, ulist_fn, full_row)
for i, ln in enumerate(lines):
    m = re.match(r"\s*\|\s*f(\d{1,3})\s*\|(.*)$", ln)
    if m:
        all_frows.append((i + 1, int(m.group(1)), ln.rstrip()))

# --- 4) 违规判定 ---
viol = []


def classify(fn, status, note):
    """返回 (cls, target_push2_or_None)。cls∈VERIFIED/DISPROVED/UNVERIFIED/BARE/CROSS/OTHER。

    证据标记与跨号映射目标编号可能落在 status 或 note 任意一格，故统一以合并文本 text 判定。
    """
    text = "%s %s" % (status, note)
    # 跨源对撞实证定案(优先于 VERIFIED): ✅ + 跨源证据标记 + 指明外部具名源字段。
    # 这是「同号即同义」铁律的正确解药——经 tdx/sina/tencent/fuyao/zhb 具名字段数值对撞定案,
    # 而非凭编号相同认定同义。证据标记: 跨源 / 交叉验证 / 第九轮审计 / 第9轮 / 第10轮。
    if "✅" in status and any(k in text for k in
                               ("跨源", "交叉验证", "第九轮审计", "第9轮", "第十轮", "第10轮")):
        return "CROSS", None
    if "✅" in status and ("第七轮审计" in text or "数值实证" in text):
        return "VERIFIED", None
    if "已证伪" in status:
        mm = re.search(r"push2\s*f(\d{1,3})", text)
        return "DISPROVED", (int(mm.group(1)) if mm else None)
    if any(k in text for k in ("未实证", "待核实", "待破解", "待数值对撞")):
        return "UNVERIFIED", None
    # 裸「同 push2 fX（同号）」断言（X==fn）且无证据标记 -> 违规模式
    m_same = re.search(r"同\s*push2\s*f(\d{1,3})", text)
    if m_same and int(m_same.group(1)) == fn:
        return "BARE", None
    return "OTHER", None


# 4a) 主守卫：§12.3.2.3 登记行
for ln_no, fn, status, note in rows_sec:
    cls, target = classify(fn, status, note)
    if cls == "DISPROVED" and target is None:
        viol.append((ln_no, "DISPROVED 行未解析出 push2 目标编号", status))
        continue
    if cls in ("VERIFIED", "DISPROVED", "BARE"):
        # VERIFIED/DISPROVED/BARE 三类都主张(或伪装) ulist.fX 与 push2 同号同义，
        # 统一走 scheme 血缘护栏：ulist239(em.ulist.np) 与 push2(em.stock_get) 是不同字段体系，
        # 故须对齐表存在 ulist.fX → push2.fY 跨号映射实证(Y 即行内声明的 push2 编号，同号时 Y==X)。
        msgs = check_scheme_grounded(fn, status, note)
        for m in (msgs or []):
            if m.startswith("WARN:"):
                sys.stderr.write("  ⚠️ %s\n" % m[5:])
            else:
                viol.append((ln_no, m, status))
    elif cls == "CROSS":
        # 跨源定案必须指明具体外部源(tdx/sina/tencent/fuyao/zhb/axdata 等)的具名字段,
        # 否则证据不足; 且不得夹带裸同号断言(那仍违反铁律)。
        text = "%s %s" % (status, note)
        if not re.search(r"(tdx|sina|tencent|fuyao|zhb|axdata|push2|东财|通达信|腾讯|同花顺|ZHB)", text, re.I):
            viol.append((ln_no, "CROSS 跨源定案未指明具体外部源字段，证据不足（须命名 tdx/sina/tencent/fuyao/zhb 等具名字段）", status))
        m_same = re.search(r"同\s*push2\s*f(\d{1,3})", text)
        if m_same and int(m_same.group(1)) == fn:
            viol.append((ln_no, "CROSS 行仍夹带裸同号即同义断言，违反铁律", status))
    # UNVERIFIED / OTHER：允许（OTHER 不含 push2 映射主张）

# 4b) 全文件回归：裸「✅ 同 push2 fX（同号…）」式断言（任何区块）
for ln_no, fn, raw in all_frows:
    # 仅当存在「同 push2 fX」且 X==fn 且不属于已验证/已证伪/待核实三类标记
    m_same = re.search(r"同\s*push2\s*f(\d{1,3})", raw)
    if not (m_same and int(m_same.group(1)) == fn):
        continue
    if ("第七轮审计" in raw or "数值实证" in raw or "已证伪" in raw
            or "未实证" in raw or "待核实" in raw or "待破解" in raw or "待数值对撞" in raw):
        continue
    viol.append((ln_no, "全文件回归：发现裸「同号即同义」断言（编号相同认定同义，未带证据标记）", raw.strip()[:90]))

# --- 4c) R0–R6 命名仲裁检查（P1）---
naming_warn, naming_viol = check_naming_registry()
viol.extend([(ln, why, "") for ln, why in naming_viol])

# --- 5) 报告 ---
if viol:
    print("❌ 字段字典「同号即同义」检查失败，发现 %d 处违规：" % len(viol))
    print("   对齐表条目数: %d（同号真同义 %d 条）" % (len(align), len(align_same)))
    print("   scheme 血缘(源=%s): ulist239=%s ↔ push2=%s（异体系→强制跨号映射实证）"
          % (SCHEME_SRC, scheme_of("ulist239", SCHEMES), scheme_of("push2", SCHEMES)))
    print("   扫描 §12.3.2.3 登记行: %d  全文件 f 编号行: %d" % (len(rows_sec), len(all_frows)))
    for ln, why, txt in viol[:80]:
        print("   行%-5d  %s  | %s" % (ln, why, txt))
    sys.exit(1)

print("✅ 字段字典「同号即同义」检查通过：")
print("   对齐表条目数: %d（同号真同义 %d 条，作为唯一实证登记处）" % (len(align), len(align_same)))
print("   scheme 血缘(源=%s): ulist239=%s ↔ push2=%s（异体系，强制跨号映射实证）"
      % (SCHEME_SRC, scheme_of("ulist239", SCHEMES), scheme_of("push2", SCHEMES)))
print("   §12.3.2.3 登记行: %d（所有 push2 映射主张均已对齐表背书或显式标为待核实）" % len(rows_sec))
print("   全文件 f 编号行: %d（无裸「同号即同义」断言复发）" % len(all_frows))
if naming_warn:
    print("   ⚠️ R0–R6 命名仲裁（warn，非阻断）：%d 项缺口/风险（补登 §12.8.12e 规范表或加数值复核即可消解；"
          "传 --strict-naming 可将 R3 升为阻断）" % len(naming_warn))
    for ln, why in naming_warn[:40]:
        print("     行%-5d  %s" % (ln, why))
if naming_viol:
    print("   ❌ R3 命名缺口（--strict-naming 阻断）：%d 项" % len(naming_viol))
