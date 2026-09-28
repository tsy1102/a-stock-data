"""
第三版对撞引擎：
1) 改进网页抽取：正则抓取 行内 "标签：值" / "标签(值)" / "买一 价 量" 等所有 (中文标签->数值) 形态；
   修正多列表(财报)只在该行后续单元格全为数值时才整体归属首列标签。
2) 对每个未知字段，逐锚样本列出"最接近的中文标签+网页实际值"(top3)，供人工裁定，
   并给出自动候选(唯一匹配优先)。
用法: py -3.12 collide3.py
"""

import os, re, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = 'C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/20260911/raw_ulist239.json'
TXTDIR = HERE + '/raw'
OUT = HERE + '/collision3_report.txt'
anchors = ['600519', '601288', '000568']


# ---------- 数值归一化 ----------
def norm_num(s):
    if s is None:
        return None
    s = str(s).strip()
    if s in ('-', '--', '', 'NULL', 'None'):
        return None
    m = re.search(r'[-+]?\d+\.?\d*', s.replace(',', ''))
    if not m:
        return None
    v = float(m.group(0))
    if '万亿' in s:
        v *= 1e12
    elif '亿' in s:
        v *= 1e8
    elif '万' in s:
        v *= 1e4
    if '%' in s:
        v /= 100.0
    return v


def value_like(tok):
    t = tok.strip()
    if not re.search(r'\d', t):
        return False
    return bool(re.match(r'^[\d,\.]+[亿万亿万%倍%户股元人天年]*$', t.replace(' ', '')))


def label_like(tok):
    t = tok.strip()
    if len(t) < 1 or len(t) > 24:
        return False
    if re.match(r'^[\d\.\-\+%]', t):
        return False
    if re.search(r'[一-鿿]', t) and not re.match(r'^\d', t):
        return True
    return False


def tol(v):
    if v == 0:
        return 1e-9
    a = abs(v)
    if a < 1:
        return 0.05
    if a < 100:
        return 0.5
    return a * 0.01


# ---------- 网页抽取 ----------
def extract_pairs(text):
    pairs = {}

    def add(lab, val):
        nv = norm_num(val)
        if nv is not None:
            pairs.setdefault(lab, set()).add(nv)

    # 1) 行内 标签：值（可能同 token 含下一标签）
    for m in re.finditer(
        r'([一-鿿A-Za-z（）()%·.\d/]+)[：:]\s*([-+]?\d[\d,\.]*\s*[亿万亿万%倍]*)', text
    ):
        add(m.group(1).strip(), m.group(2))
    # 2) 括号 标签(值)
    for m in re.finditer(r'([一-鿿]+)\(\s*([-+]?\d[\d,\.]*\s*[亿万亿万%]*)\s*\)', text):
        add(m.group(1).strip(), m.group(2))
    # 3) 买一/卖五 价 量
    for m in re.finditer(r'(买[一二三四五]|卖[一二三四五])\s*([\d\.]+)', text):
        add(m.group(1), m.group(2))
    # 4) 多列财报表：首列标签 + 后续全为数值
    for line in text.split('\n'):
        toks = [t.strip() for t in line.split('\t') if t.strip() != '']
        if len(toks) < 2:
            continue
        if label_like(toks[0]) and value_like(toks[1]) and (len(toks) < 3 or value_like(toks[2])):
            for t in toks[1:]:
                if value_like(t):
                    add(toks[0], t)
        # 5) 兼容 tab 成对
        for i in range(len(toks) - 1):
            if label_like(toks[i]) and value_like(toks[i + 1]):
                add(toks[i], toks[i + 1])
    return pairs


# 加载网页
web = {}
for code in anchors:
    merged = {}
    for fn in glob.glob(f"{TXTDIR}/*_{code}.txt"):
        try:
            txt = open(fn, encoding='utf-8').read()
        except:
            continue
        for lab, vs in extract_pairs(txt).items():
            merged.setdefault(lab, set()).update(vs)
    web[code] = merged

# 未知字段
fd = (
    open('C:/Tencent/WorkBuddy/a-stock-data/docs/field_dict.md', encoding='utf-8')
    .read()
    .split('\n')
)
start = next(i for i, l in enumerate(fd) if '12.3.2.3 ulist239' in l)
unknown = []
i = start
while i < len(fd):
    ln = fd[i]
    if i > start and ln.startswith('#### ') and '12.3.2.3' not in ln:
        break
    m = re.match(r'\|\s*(f\d+)\s*\|\s*(.*?)\s*\|', ln)
    if m and '待破解' in m.group(2):
        unknown.append(m.group(1))
    i += 1

u = json.load(open(RAW, encoding='utf-8'))
stocks = u['stocks']

out = []
for f in sorted(unknown, key=lambda x: int(x[1:])):
    out.append(f"==== {f} ====")
    for code in anchors:
        v = stocks[code]['data'].get(f)
        if v in (None, '-', '--'):
            out.append(f"  {code}: EMPTY(-)")
            continue
        try:
            vn = float(v)
        except:
            out.append(f"  {code}: STR={v!r}")
            continue
        # 找最接近的网页标签
        cands = []
        for lab, vs in web[code].items():
            for wv in vs:
                if wv is None:
                    continue
                d = abs(vn - wv)
                if d <= tol(max(abs(vn), abs(wv))):
                    cands.append((d, lab, wv))
        cands.sort()
        top = cands[:3]
        s = "; ".join(f"{lab}={wv:g}(Δ{d:.4g})" for d, lab, wv in top) if top else "NOMATCH"
        out.append(f"  {code}: ulist={vn:g} -> {s}")
    out.append("")

open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
print(f"\n[done] {len(unknown)} 字段, 报告: {OUT}")
