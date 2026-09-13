import os, json

BASE = 'C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/20260911'
u = json.load(open(os.path.join(BASE, 'raw_ulist239.json'), encoding='utf-8'))

def walk(o, depth=0, path=''):
    """Find the structure: how stocks and fields are stored."""
    if isinstance(o, dict):
        ks = list(o.keys())
        print(f"{'  '*depth}{path} dict[{len(ks)}]: {ks[:6]}{'...' if len(ks)>6 else ''}")
        if depth < 2:
            for k in ks[:3]:
                walk(o[k], depth+1, f"{path}.{k}")
    elif isinstance(o, list):
        print(f"{'  '*depth}{path} list[{len(o)}]")
        if o and depth < 2:
            walk(o[0], depth+1, f"{path}[0]")
    else:
        s = str(o)
        print(f"{'  '*depth}{path} = {s[:60]}")

print("=== TOP ===")
walk(u)

# Save top-level keys for inspection
print("\n=== TOP KEYS ===")
print(list(u.keys()) if isinstance(u, dict) else type(u))
