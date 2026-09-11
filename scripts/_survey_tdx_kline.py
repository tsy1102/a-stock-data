import glob, os, json
p = 'C:/Users/tsy11/.workbuddy/projects/c-Tencent-WorkBuddy/aff6d326-10e5-4354-a7a7-5dbea6d60248/tool-results'
fs = sorted(glob.glob(os.path.join(p, 'mcp-tdx-connector-tdx_kline-*.txt')))
print("Total tdx_kline txt files:", len(fs))
for f in fs:
    print(os.path.basename(f), os.path.getsize(f))
print("---- existing raw_tdx_kline_beta.json ----")
jf = 'docs/field_verification/raw_tdx_kline_beta.json'
if os.path.exists(jf):
    d = json.load(open(jf, encoding='utf-8'))
    print("codes present:", len(d))
    for c, v in d.items():
        print(c, "kept=%d unit=%s d0=%s d1=%s" % (v['n_kept'], v['unit'], v['dates'][0] if v['dates'] else None, v['dates'][-1] if v['dates'] else None))
else:
    print("NOT FOUND")
