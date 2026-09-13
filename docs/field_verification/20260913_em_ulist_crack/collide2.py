"""
第二轮值级对撞：把采集脚本 raw_ulist239.json 中 105 个未知字段，与 CDP 抓取的东方财富
网页(报价页 + F10 财务分析 主要指标/资产负债表/利润表/现金流量表)做真实值级对撞。
方法：从网页文本抽取 (中文标签 -> [归一化数值列表])；对每字段在 3 锚样本取值，
匹配网页标签；唯一匹配 + >=2/3 锚样本 -> 高置信定案。
"""
import os, re, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = 'C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/20260911/raw_ulist239.json'
TXTDIR = HERE + '/raw'
OUT = HERE + '/collision2_out.txt'

anchors = ['600519', '601288', '000568']

# ---------- 数值归一化 ----------
def norm_num(s):
    if s is None: return None
    s = str(s).strip()
    if s in ('-', '--', '', 'NULL', 'None'): return None
    # 提取首个数字片段（容忍 ↓ - 等装饰）
    m = re.search(r'[-+]?\d+\.?\d*', s.replace(',', ''))
    if not m: return None
    v = float(m.group(0))
    if '万亿' in s: v *= 1e12
    elif '亿' in s: v *= 1e8
    elif '万' in s: v *= 1e4
    if '%' in s: v /= 100.0
    return v

def value_like(tok):
    t = tok.strip()
    if not re.search(r'\d', t): return False
    if re.match(r'^[\d,\.]+[亿万亿万%倍户股元人天年]*$', t.replace(' ','')): return True
    return False

def label_like(tok):
    t = tok.strip()
    if len(t) < 1 or len(t) > 24: return False
    if re.match(r'^[\d\.\-\+%]', t): return False
    # 含中文且不以数字开头
    if re.search(r'[一-鿿]', t) and not re.match(r'^\d', t): return True
    return False

def tol(v):
    if v == 0: return 1e-9
    a = abs(v)
    if a < 1: return 0.05
    if a < 100: return 0.5
    return a * 0.01

# ---------- 从网页文本抽取 (label, [values]) ----------
def extract_pairs(text):
    """返回 {label: set(norm_values)}"""
    pairs = {}
    # 统一分隔符
    text = text.replace('：', '\t').replace(':', '\t').replace('|', '\t')
    for line in text.split('\n'):
        # 跳过表头/纯装饰
        toks = [t.strip() for t in line.split('\t') if t.strip() != '']
        if len(toks) < 2: continue
        # pair-based: 相邻 (label, value)
        for i in range(len(toks)-1):
            if label_like(toks[i]) and value_like(toks[i+1]):
                pairs.setdefault(toks[i], set()).add(norm_num(toks[i+1]))
        # multi-column: 首列是 label 且后面有多个数值
        if label_like(toks[0]):
            vals = [norm_num(t) for t in toks[1:] if value_like(t)]
            if len(vals) >= 2:
                pairs.setdefault(toks[0], set()).update(vals)
    return pairs

# ---------- 加载所有网页文本 ----------
web = {}  # code -> {label: set(values)}
for code in anchors:
    merged = {}
    for fn in glob.glob(f"{TXTDIR}/*_{code}.txt"):
        try:
            txt = open(fn, encoding='utf-8').read()
        except Exception:
            continue
        pr = extract_pairs(txt)
        for lab, vs in pr.items():
            merged.setdefault(lab, set()).update(vs)
    web[code] = merged

# ---------- 加载 ulist 未知字段 ----------
fd = open('C:/Tencent/WorkBuddy/a-stock-data/docs/field_dict.md', encoding='utf-8').read().split('\n')
start = next(i for i,l in enumerate(fd) if '12.3.2.3 ulist239' in l)
unknown = []
i = start
while i < len(fd):
    ln = fd[i]
    if i > start and ln.startswith('#### ') and '12.3.2.3' not in ln: break
    m = re.match(r'\|\s*(f\d+)\s*\|\s*(.*?)\s*\|', ln)
    if m and '待破解' in m.group(2): unknown.append(m.group(1))
    i += 1

u = json.load(open(RAW, encoding='utf-8'))
stocks = u['stocks']

# ---------- 对每个未知字段做对撞 ----------
lines_out = []
summary = []
for f in sorted(unknown, key=lambda x: int(x[1:])):
    cand_per_stock = {}
    for code in anchors:
        v = stocks[code]['data'].get(f)
        if v in (None, '-', '--'):
            cand_per_stock[code] = ('EMPTY', set())
            continue
        try: vn = float(v)
        except: 
            # 字符串类字段（代码/名称/行业）
            cand_per_stock[code] = ('STR', str(v))
            continue
        matched = set()
        for lab, vs in web[code].items():
            for wv in vs:
                if wv is None: continue
                if abs(vn - wv) <= tol(max(abs(vn), abs(wv))):
                    matched.add(lab)
        cand_per_stock[code] = ('NUM', matched)
    # 汇总
    nums = {c: d for c, (t, d) in cand_per_stock.items() if t == 'NUM'}
    strs = {c: d for c, (t, d) in cand_per_stock.items() if t == 'STR'}
    empt = [c for c, (t, d) in cand_per_stock.items() if t == 'EMPTY']
    # 找在所有有值样本中唯一的共同标签
    common = None
    if nums:
        sets = [d for d in nums.values()]
        common = set.intersection(*sets) if sets else set()
    n_unique = sum(1 for d in nums.values() if len(d) == 1)
    # 决定候选
    if strs and len(set(strs.values())) == 1:
        final = f"STR={list(strs.values())[0]}"
        conf = 'STR-OK'
    elif common:
        if len(common) == 1:
            final = 'UNIQUE:' + list(common)[0]
            conf = 'HIGH' if n_unique >= 2 else 'MED'
        else:
            # common 多，但看是否有某标签在多数样本唯一
            final = 'MULTI:' + '/'.join(sorted(common)[:4])
            conf = 'LOW'
    elif n_unique >= 2:
        # 各样本唯一但标签不同 -> 可能单位/口径差异
        uniqs = {c: list(d)[0] for c, d in nums.items() if len(d) == 1}
        final = 'PERSTOCK:' + '/'.join(f"{c}={v}" for c, v in uniqs.items())
        conf = 'DIVERGE'
    else:
        final = 'NOMATCH'
        conf = 'NONE'
    summary.append((f, conf, final, cand_per_stock))
    lines_out.append(f"{f:5s} [{conf}] {final}")

open(OUT, 'w', encoding='utf-8').write('\n'.join(lines_out))
print('\n'.join(lines_out))
print(f"\n总未知字段: {len(unknown)}  已落盘: {OUT}")
