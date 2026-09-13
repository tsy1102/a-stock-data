import re

FD = 'C:/Tencent/WorkBuddy/a-stock-data/docs/field_dict.md'
lines = open(FD, encoding='utf-8').read().split('\n')

# find section 12.3.2.3
start = None
for i, ln in enumerate(lines):
    if '12.3.2.3 ulist239' in ln:
        start = i
        break
print("section start line:", start)

# extract table rows until next '#### ' or end of ulist block
rows = {}
i = start
while i < len(lines):
    ln = lines[i]
    if i > start and ln.startswith('#### ') and '12.3.2.3' not in ln:
        # next section
        break
    m = re.match(r'\|\s*(f\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', ln)
    if m:
        f = m.group(1)
        status = m.group(2)
        note = m.group(3)
        rows[f] = (status, note)
    i += 1

print("total rows parsed:", len(rows))
# classify
unknown = [f for f, (s, n) in rows.items() if '待破解' in s]
cracked = [f for f, (s, n) in rows.items() if '待破解' not in s]
print("\n=== UNKNOWN (待破解) count:", len(unknown))
print(sorted(unknown, key=lambda x: int(x[1:])))
print("\n=== ALREADY CRACKED count:", len(cracked))
for f in sorted(cracked, key=lambda x: int(x[1:])):
    print(f, rows[f][0])
