import glob, os, json, math
from json import JSONDecoder

ROOT = 'C:/Tencent/WorkBuddy/a-stock-data'
RES = 'C:/Users/tsy11/.workbuddy/projects/c-Tencent-WorkBuddy/aff6d326-10e5-4354-a7a7-5dbea6d60248/tool-results'
BETA = json.load(open(ROOT + '/docs/field_verification/raw_tdx_kline_beta.json', encoding='utf-8'))
TX = json.load(open(ROOT + '/docs/field_verification/20260908/raw_tencent.json', encoding='utf-8'))['stocks']

# parse 中证全指 file
fz = max(glob.glob(os.path.join(RES, 'mcp-tdx-connector-tdx_kline-1788917119088-644441.txt')))
txt = open(fz, encoding='utf-8', errors='replace').read()
i = txt.find('{'); obj, _ = JSONDecoder().raw_decode(txt, i)
rows = obj.get('Rows') or []
cs_close, cs_date = [], []
for r in rows:
    if float(r.get('Volume') or 0) == 0: continue
    cs_date.append(r.get('Data')); cs_close.append(float(r.get('Close')))
BETA['000985'] = {'n_kept': len(cs_close), 'unit': obj.get('AttachInfo',{}).get('Unit'),
                  'name': '中证全指', 'dates': cs_date, 'closes': cs_close, 'vols': [0]*len(cs_close)}
print("中证全指 000985 kept=%d d0=%s d1=%s" % (len(cs_close), cs_date[0], cs_date[-1]))

def num(x):
    try: return float(x) if x is not None else None
    except Exception: return None

def daily_returns(dates, closes):
    return [(dates[i], (closes[i]-closes[i-1])/closes[i-1]) for i in range(1,len(closes)) if closes[i-1] and closes[i]]

def beta_of(stock_ret, mkt_map):
    common = sorted(set(d for d,_ in stock_ret) & set(mkt_map.keys()))
    xs=[mkt_map[d] for d in common]; ys=[v for d,v in stock_ret if d in mkt_map]
    if len(xs)<30: return None
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys)); vx=sum((x-mx)**2 for x in xs)
    return cov/vx if vx>0 else None

def pearson(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    return cov/(sx*sy) if sx*sy else None

def spearman(xs,ys):
    def rk(a):
        sa=sorted(range(len(a)),key=lambda i:a[i]); r=[0]*len(a); i=0
        while i<len(a):
            j=i
            while j+1<len(a) and a[sa[j+1]]==a[sa[i]]: j+=1
            avg=(i+j)/2.0
            for k in range(i,j+1): r[sa[k]]=avg
            i=j+1
        return r
    return pearson(rk(xs),rk(ys))

def linfit(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    b=sxy/sxx; a=my-b*mx
    pred=[a+b*x for x in xs]; sst=sum((y-my)**2 for y in ys)
    ssr=sum((y-p)**2 for y,p in zip(ys,pred))
    return a,b,(1-ssr/sst if sst else None)

mkt_ret = dict(daily_returns(BETA['000300']['dates'], BETA['000300']['closes']))
broad_ret = dict(daily_returns(BETA['000985']['dates'], BETA['000985']['closes']))
ind = [c for c in BETA if c not in ('000300','000985')]
ew = {}
for c in ind:
    for d,v in daily_returns(BETA[c]['dates'], BETA[c]['closes']):
        ew.setdefault(d,[]).append(v)
ew_ret = {d: sum(v)/len(v) for d,v in ew.items() if v}

rows = []
for c in ind:
    sr = daily_returns(BETA[c]['dates'], BETA[c]['closes'])
    bh = beta_of(sr, mkt_ret); bb = beta_of(sr, broad_ret); be = beta_of(sr, ew_ret)
    f = TX.get(c,{}).get('fields'); t56 = num(f[56]) if isinstance(f,list) and len(f)>86 else None
    rows.append((c,bh,bb,be,t56))

bm = {'沪深300':mkt_ret, '中证全指':broad_ret, '等权':ew_ret}
print("\ncode        B_hs300  B_全指   B_等权   tx56")
for c,bh,bb,be,t in rows:
    print("%-10s  %7.3f  %7.3f  %7.3f  %s"%(c, bh or 0,bb or 0,be or 0, ("%.3f"%t) if t is not None else "None"))

print("\n=== Collision tx[56] vs Beta(benchmark) ===")
for name,mp in bm.items():
    xs=[r[1+rk] for rk,mm in enumerate([mkt_ret,broad_ret,ew_ret]) if mm is mp for r in rows if r[1+rk] is not None and r[4] is not None]
    # map properly
    idx = list(bm.keys()).index(name)
    xs=[r[1+idx] for r in rows if r[1+idx] is not None and r[4] is not None]
    ys=[r[4] for r in rows if r[1+idx] is not None and r[4] is not None]
    a,b,r2=linfit(xs,ys)
    pr=pearson(xs,ys); sp=spearman(xs,ys)
    print("%-8s n=%2d fit tx56=%.3f+%.3f*B R2=%.4f r=%.4f rho=%.4f"%(name,len(xs),a,b,r2 or 0,pr,sp))
    # rounded hit rate (0.01)
    hit=sum(1 for x,y in zip(xs,ys) if abs(round(y,2)-round(a+b*x,2))<=0.01)
    print("         rounded(0.01) hit=%d/%d"%(hit,len(xs)))

# diagnostics: cumulative returns
def cumret(closes):
    return (closes[-1]/closes[0]-1)*100
print("\n=== Diagnostics full-window cumulative return %% ===")
for c in ['000300','000985','601288','600519','688589']:
    if c in BETA:
        print("%-8s %s = %.1f%%"%(c, BETA[c].get('name',c), cumret(BETA[c]['closes'])))
print("农业银行 vs 沪深300 daily-return Pearson (sanity):",
      pearson([v for d,v in daily_returns(BETA['601288']['dates'],BETA['601288']['closes']) if d in mkt_ret],
              [mkt_ret[d] for d,v in daily_returns(BETA['601288']['dates'],BETA['601288']['closes']) if d in mkt_ret]))

json.dump(BETA, open(ROOT+'/docs/field_verification/raw_tdx_kline_beta.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("\nupdated raw_tdx_kline_beta.json with 000985")
