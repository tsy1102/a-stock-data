import os
import re

d = r"D:\GitHub\test\scratch\zhb_20260713"
targets = ["1256", "19405", "4399", "15563", "2097", "17484", "1556", "1748"]
found = {}

for file in os.listdir(d):
    path = os.path.join(d, file)
    if not os.path.isfile(path): continue
    try:
        with open(path, "r", encoding="gbk", errors="ignore") as f:
            for line in f:
                if "600519" in line or "000001" in line or "300750" in line:
                    for t in targets:
                        if t in line:
                            found.setdefault(file, []).append((t, line.strip()))
    except Exception:
        pass

for file, lines in found.items():
    print(f"--- {file} ---")
    for t, l in lines:
        print(f"Found {t} in: {l}")
