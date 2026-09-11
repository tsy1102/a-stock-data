import glob, os, json
from json import JSONDecoder

ROOT = 'C:/Tencent/WorkBuddy/a-stock-data'
RES = 'C:/Users/tsy11/.workbuddy/projects/c-Tencent-WorkBuddy/aff6d326-10e5-4354-a7a7-5dbea6d60248/tool-results'
OUT = os.path.join(ROOT, 'docs/field_verification/raw_tdx_kline_beta.json')

dec = JSONDecoder()
files = sorted(glob.glob(os.path.join(RES, 'mcp-tdx-connector-tdx_kline-*.txt')))

out = {}
for f in files:
    txt = open(f, encoding='utf-8', errors='replace').read()
    i = txt.find('{')
    if i < 0:
        print("NO JSON in", os.path.basename(f)); continue
    obj, _ = dec.raw_decode(txt, i)
    code = obj.get('Code')
    rows = obj.get('Rows') or []
    att = obj.get('AttachInfo') or {}
    unit = att.get('Unit')
    name = att.get('Name')
    hqdate = att.get('HqDate')
    series = []
    n_empty = 0
    for r in rows:
        vol = float(r.get('Volume') or 0)
        close = float(r.get('Close') or 0)
        if vol == 0:
            n_empty += 1
            continue
        series.append((r.get('Data'), close, vol))
    dates = [s[0] for s in series]
    closes = [s[1] for s in series]
    vols = [s[2] for s in series]
    out[code] = {
        'n_bars': len(rows), 'n_empty': n_empty, 'n_kept': len(series),
        'unit': unit, 'name': name, 'hqdate': hqdate,
        'dates': dates, 'closes': closes, 'vols': vols,
    }
    print("%s name=%-8s unit=%s kept=%d empty=%d d0=%s d1=%s" % (
        code, name, unit, len(series), n_empty, dates[0] if dates else None, dates[-1] if dates else None))

json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("\nWROTE", OUT, "codes=", len(out))
