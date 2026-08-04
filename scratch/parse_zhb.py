import sys

with open(r"D:\GitHub\test\scratch\zhb_20260713\tdxstat.cfg", "r", encoding="gbk", errors="ignore") as f:
    for line in f:
        if "600519" in line or "000001" in line or "300750" in line:
            parts = line.strip().split("|")
            if len(parts) > 1 and parts[1] in ("600519", "000001", "300750"):
                print(f"--- {parts[1]} tdxstat.cfg ---")
                for i, p in enumerate(parts):
                    print(f"[{i:02d}]: {p}")

print("\n")
with open(r"D:\GitHub\test\scratch\zhb_20260713\tdxstat2.cfg", "r", encoding="gbk", errors="ignore") as f:
    for line in f:
        if "600519" in line or "000001" in line or "300750" in line:
            parts = line.strip().split("|")
            if len(parts) > 1 and parts[1] in ("600519", "000001", "300750"):
                print(f"--- {parts[1]} tdxstat2.cfg ---")
                for i, p in enumerate(parts):
                    print(f"[{i:02d}]: {p}")
