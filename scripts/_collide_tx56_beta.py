import json, math
from json import JSONDecoder

ROOT = 'C:/Tencent/WorkBuddy/a-stock-data'
BETA = json.load(open(ROOT + '/docs/field_verification/raw_tdx_kline_beta.json', encoding='utf-8'))
TX = json.load(open(ROOT + '/docs/field_verification/20260908/raw_tencent.json', encoding='utf-8'))['stocks']

def num(x):
    try:
        if x is None: return None
        return float(x)
    except Exception:
        return None

def daily_returns(dates, closes):
    r = []
    for i in range(1, len(closes)):
        p0, p1 = closes[i-1], closes[i]
        if p0 and p1:
            r.append((dates[i], (p1 - p0)/p0))
    return r

# benchmark: 沪深300
mkt_dates = BETA['000300']['dates']
mkt_closes = BETA['000300']['closes']
mkt_ret = dict(daily_returns(mkt_dates, mkt_closes))

# equal-weight proxy from all individual stocks (exclude benchmark + 北交所)
ind_codes = [c for c in BETA if c != '000300']
ew_ret = {}
for c in ind_codes:
    rd = daily_returns(BETA[c]['dates'], BETA[c]['closes'])
    for d, v in rd:
        ew_ret.setdefault(d, []).append(v)
ew_mkt_ret = {d: sum(v)/len(v) for d, v in ew_ret.items() if v}

def beta_of(stock_ret, mkt_ret_map):
    # align common dates
    common = sorted(set(d for d,_ in stock_ret) & set(mkt_ret_map.keys()))
    xs = [mkt_ret_map[d] for d in common]   # market
    ys = [v for d,v in stock_ret if d in mkt_ret_map]
    if len(xs) < 30: return None, None, len(xs)
    mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
    cov = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    vx = sum((x-mx)**2 for x in xs)
    if vx <= 0: return None, None, len(xs)
    return cov/vx, len(xs), common

def pearson(xs, ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    return cov/(sx*sy) if sx*sy else None

def spearman(xs, ys):
    def rank(a):
        sa=sorted(range(len(a)), key=lambda i:a[i])
        r=[0]*len(a); i=0
        while i<len(a):
            j=i
            while j+1<len(a) and a[sa[j+1]]==a[sa[i]]: j+=1
            avg=(i+j)/2.0
            for k in range(i,j+1): r[sa[k]]=avg
            i=j+1
        return r
    return pearson(rank(xs), rank(ys))

# collect per-stock Beta vs both benchmarks
rows = []
tx56_map = {}
for c in ind_codes:
    sr = daily_returns(BETA[c]['dates'], BETA[c]['closes'])
    b_hs300, n_hs, _ = beta_of(sr, mkt_ret)
    b_ew, n_ew, _ = beta_of(sr, ew_mkt_ret)
    # tx[56]
    f = TX.get(c, {}).get('fields')
    t56 = num(f[56]) if isinstance(f, list) and len(f) > 86 else None
    tx56_map[c] = t56
    rows.append((c, b_hs300, b_ew, t56))

print("code        BetaHS300  BetaEW     tx56")
print("-------------------------------------------")
for c, bhs, bew, t in rows:
    print("%-10s  %8.4f  %8.4f  %s" % (c, bhs if bhs is not None else 0, bew if bew is not None else 0, ("%.4f"%t) if t is not None else "None"))

# Collision: tx56 vs BetaHS300
xs_hs = [r[1] for r in rows if r[1] is not None and r[3] is not None]
ys_tx = [r[3] for r in rows if r[1] is not None and r[3] is not None]
xs_ew = [r[2] for r in rows if r[2] is not None and r[3] is not None]

def linfit(xs, ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    b=sxy/sxx; a=my-b*mx
    pred=[a+b*x for x in xs]
    ss_res=sum((y-p)**2 for y,p in zip(ys,pred)); ss_tot=sum((y-my)**2 for y in ys)
    r2=1-ss_res/ss_tot if ss_tot else None
    return a,b,r2

a_hs,b_hs,r2_hs = linfit(xs_hs, ys_tx)
a_ew,b_ew,r2_ew = linfit(xs_ew, ys_tx)
pr_hs = pearson(xs_hs, ys_tx); pr_ew = pearson(xs_ew, ys_tx)
sp_hs = spearman(xs_hs, ys_tx); sp_ew = spearman(xs_ew, ys_tx)

print("\n=== Collision tx[56] vs TDX-Beta (沪深300 benchmark) ===")
print("n=%d  fit: tx56 = %.4f + %.4f*Beta   R2=%.4f" % (len(xs_hs), a_hs, b_hs, r2_hs if r2_hs else 0))
print("Pearson r=%.4f  Spearman rho=%.4f" % (pr_hs, sp_hs))
print("\n=== Collision tx[56] vs TDX-Beta (equal-weight proxy) ===")
print("n=%d  fit: tx56 = %.4f + %.4f*Beta   R2=%.4f" % (len(xs_ew), a_ew, b_ew, r2_ew if r2_ew else 0))
print("Pearson r=%.4f  Spearman rho=%.4f" % (pr_ew, sp_ew))

# residual precision check for the best fit
print("\n=== Residual precision (tx56 - (a+b*Beta)) ===")
best_xs, best_a, best_b = (xs_hs, a_hs, b_hs)
maxabs=0; within1pct=0
for (c,_,_,t),x in zip([r for r in rows if r[1] is not None and r[3] is not None], best_xs):
    resid = t - (best_a + best_b*x)
    rel = abs(resid)/abs(t) if t else 0
    if abs(resid)>maxabs: maxabs=abs(resid)
    if rel<=0.01: within1pct+=1
print("HS300 fit: max|resid|=%.6f  within1%%=%d/%d" % (maxabs, within1pct, len(best_xs)))
