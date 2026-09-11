import glob, os, json
from json import JSONDecoder

p = 'C:/Users/tsy11/.workbuddy/projects/c-Tencent-WorkBuddy/aff6d326-10e5-4354-a7a7-5dbea6d60248/tool-results'
fs = sorted(glob.glob(os.path.join(p, 'mcp-tdx-connector-tdx_kline-*.txt')))
dec = JSONDecoder()

out = {}
for f in fs:
    try:
        txt = open(f, encoding='utf-8', errors='replace').read()
    except Exception as e:
        print("skip read", f, e)
        continue
    i = txt.find('{')
    if i < 0:
        continue
    try:
        obj, _ = dec.raw_decode(txt, i)
    except Exception as e:
        print("skip parse", os.path.basename(f), e)
        continue
    code = obj.get('Code')
    rows = obj.get('Rows') or []
    ai = obj.get('AttachInfo', {}) or {}
    unit = ai.get('Unit')
    dates, opens, highs, lows, closes, amounts, volumes, rawvols, rawamts = [], [], [], [], [], [], [], [], []
    n_empty = 0
    for r in rows:
        try:
            vol = float(r.get('Volume') or 0)
            amt = float(r.get('Amount') or 0)
            rawvol = float(r.get('RawVolume') or 0)
            rawamt = float(r.get('RawAmount') or 0)
            o = float(r.get('Open') or 0); h = float(r.get('High') or 0)
            l = float(r.get('Low') or 0); c = float(r.get('Close') or 0)
        except Exception:
            continue
        dates.append(r.get('Data'))
        opens.append(o); highs.append(h); lows.append(l); closes.append(c)
        amounts.append(amt); volumes.append(vol)
        rawvols.append(rawvol); rawamts.append(rawamt)
        if vol == 0:
            n_empty += 1
    if code in out:
        # 同 code 多文件: 保留 bars 更多者(更完整)
        if len(rows) <= out[code]['n_bars']:
            continue
    out[code] = {
        'name': ai.get('Name'),
        'unit': unit,
        'n_bars': len(rows),
        'n_empty': n_empty,
        'n_kept': len([v for v in volumes if v > 0]),
        'dates': dates, 'opens': opens, 'highs': highs, 'lows': lows, 'closes': closes,
        'amounts': amounts, 'volumes': volumes, 'rawvolumes': rawvols, 'rawamounts': rawamts,
    }

dst = 'docs/field_verification/raw_tdx_kline_full.json'
os.makedirs(os.path.dirname(dst), exist_ok=True)
json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("written", dst, "| codes:", len(out))
for c in ('000300', '000985'):
    if c in out:
        print(c, "kept=%d unit=%s lastdate=%s" % (out[c]['n_kept'], out[c]['unit'], out[c]['dates'][-1]))
# 校验最新非空 bar 的 VWAP 候选量级
print("== VWAP 量级抽检(最新非空bar) ==")
for c in ('600519', '000568', '300031'):
    if c not in out:
        continue
    vols = out[c]['volumes']; amts = out[c]['amounts']
    rawv = out[c]['rawvolumes']; rawa = out[c]['rawamounts']
    # 找最新非空
    idx = max(i for i in range(len(vols)) if vols[i] > 0)
    v1 = amts[idx] / vols[idx] if vols[idx] else None
    v2 = rawa[idx] / rawv[idx] if rawv[idx] else None
    print(c, "date=%s VWAP(amt/vol)=%s VWAP(rawamt/rawvol)=%s close=%s" % (
        out[c]['dates'][idx], v1, v2, out[c]['closes'][idx]))
