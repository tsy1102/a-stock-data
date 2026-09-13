import os, json

BASE = 'C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/20260911'
u = json.load(open(os.path.join(BASE, 'raw_ulist239.json'), encoding='utf-8'))
stocks = u['stocks']
print("n stocks:", len(stocks))
code0 = '600519'
d0 = stocks[code0]['data']
print("n_fields:", stocks[code0]['n_fields'], "len data:", len(d0))
keys = sorted(d0.keys(), key=lambda k: int(k[1:]) if k[1:].isdigit() else 9999)
print("total field keys:", len(keys))
print("first 30 keys:", keys[:30])
print("last 20 keys:", keys[-20:])
# show all keys for reference
print("\n=== ALL KEYS ===")
print(keys)
