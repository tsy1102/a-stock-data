import os, json

BASE = 'C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/20260911'
u = json.load(open(os.path.join(BASE, 'raw_ulist239.json'), encoding='utf-8'))
stocks = u['stocks']

# unknown set from field_dict parse
FD = 'C:/Tencent/WorkBuddy/a-stock-data/docs/field_dict.md'
import re

flines = open(FD, encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(flines) if '12.3.2.3 ulist239' in l)
unknown = []
i = start
while i < len(flines):
    ln = flines[i]
    if i > start and ln.startswith('#### ') and '12.3.2.3' not in ln:
        break
    m = re.match(r'\|\s*(f\d+)\s*\|\s*(.*?)\s*\|', ln)
    if m and '待破解' in m.group(2):
        unknown.append(m.group(1))
    i += 1

anchors = ['600519', '601288', '000568']
print("unknown count:", len(unknown))
for f in sorted(unknown, key=lambda x: int(x[1:])):
    vals = []
    for c in anchors:
        v = stocks[c]['data'].get(f, 'NA')
        vals.append(str(v))
    print(f"{f:5s} | " + " | ".join(f"{anchors[k]}:{vals[k]}" for k in range(3)))
