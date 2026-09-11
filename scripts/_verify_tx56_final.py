import json, math
ROOT = 'C:/Tencent/WorkBuddy/a-stock-data'
BETA = json.load(open(ROOT + '/docs/field_verification/raw_tdx_kline_beta.json', encoding='utf-8'))
TX = json.load(open(ROOT + '/docs/field_verification/20260908/raw_tencent.json', encoding='utf-8'))['stocks']

def num(x):
    try: return float(x) if x is not None else None
    except Exception: return None

def dret(dates, closes):
    return {dates[i]: (closes[i]-closes[i-1])/closes[i-1] for i in range(1,len(closes)) if closes[i-1] and closes[i]}

mkt = dret(BETA['000300']['dates'], BETA['000300']['closes'])
broad = dret(BETA['000985']['dates'], BETA['000985']['closes'])
ind = [c for c in BETA if c not in ('000300','000985')]

def beta_of(sr, mp):
    common = sorted(set(sr) & set(mp))
    xs=[mp[d] for d in common]; ys=[sr[d] for d in common]
    if len(xs)<30: return None
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys)); vx=sum((x-mx)**2 for x in xs)
    return cov/vx if vx>0 else None

def pearson(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    return cov/(sx*sy) if sx*sy else None

rows=[]
for c in ind:
    sr=dret(BETA[c]['dates'], BETA[c]['closes'])
    bh=beta_of(sr,mkt); bb=beta_of(sr,broad)
    f=TX.get(c,{}).get('fields'); t56=num(f[56]) if isinstance(f,list) and len(f)>86 else None
    rows.append((c,bh,bb,t56))

# choose broad as best benchmark
xs=[r[2] for r in rows if r[2] is not None and r[3] is not None]
ys=[r[3] for r in rows if r[2] is not None and r[3] is not None]
n=len(xs)
mx=sum(xs)/n; my=sum(ys)/n
sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
b=sxy/sxx; a=my-b*mx
pred=[a+b*x for x in xs]; ssr=sum((y-p)**2 for y,p in zip(ys,pred)); sst=sum((y-my)**2 for y in ys)
r2=1-ssr/sst; pr=pearson(xs,ys)

# leave-one-out stability
loo=[]
for k in range(n):
    xx=[xs[j] for j in range(n) if j!=k]; yy=[ys[j] for j in range(n) if j!=k]
    mmx=sum(xx)/len(xx); mmy=sum(yy)/len(yy)
    bb_=sum((x-mmx)*(y-mmy) for x,y in zip(xx,yy))/sum((x-mmx)**2 for x in xx)
    loo.append(pearson(xx,yy))
min_loo=min(loo)

print("=== FINAL: tx[56] vs Beta_中证全指(n=%d) ==="%n)
print("fit: tx56 = %.4f + %.4f*B   R2=%.4f  Pearson=%.4f"%(a,b,r2,pr))
print("leave-one-out Pearson min = %.4f (all >0.6: %s)"%(min_loo, all(v>0.6 for v in loo)))
print("\nper-stock residual table:")
print("code        tx56    Beta全指  pred    resid   rel%")
maxabs=0
for r,(c,_,bb,t) in zip(range(n),[(c,_,bb,t) for c,_,bb,t in rows if bb is not None and t is not None]):
    p=a+b*bb; resid=t-p; rel=abs(resid)/abs(t)*100 if t else 0
    maxabs=max(maxabs,abs(resid))
    print("%-10s %6.3f  %6.3f  %6.3f  %6.3f  %5.1f"%(c,t,bb,p,resid,rel))
print("max|resid|=%.4f"%maxabs)

# also hs300+spearman for the record
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
xs_h=[r[1] for r in rows if r[1] is not None and r[3] is not None]
ys_h=[r[3] for r in rows if r[1] is not None and r[3] is not None]
print("\nvs 沪深300: Pearson=%.4f Spearman=%.4f"%(pearson(xs_h,ys_h), spearman(xs_h,ys_h)))
print("vs 中证全指: Pearson=%.4f Spearman=%.4f"%(pr, spearman(xs,ys)))

ev = {
  'benchmark':'中证全指(000985, TDX前复权日K)',
  'n':n, 'fit_a':a, 'fit_b':b, 'r2':r2, 'pearson':pr, 'spearman':spearman(xs,ys),
  'loo_min':min_loo, 'max_abs_resid':maxabs,
  'per_stock':[{'code':c,'tx56':t,'beta_broad':bb,'pred':a+b*bb,'resid':t-(a+b*bb)} for c,_,bb,t in rows if bb is not None and t is not None],
  'hs300':{'pearson':pearson(xs_h,ys_h),'spearman':spearman(xs_h,ys_h)},
}
json.dump(ev, open(ROOT+'/docs/field_verification/tx56_collision_evidence.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("\nwrote tx56_collision_evidence.json")
