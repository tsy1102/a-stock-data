import os
import sys

d = r"D:\GitHub\test\scratch\zhb_20260713"
out = []
for file in sorted(os.listdir(d)):
    path = os.path.join(d, file)
    if os.path.isfile(path):
        size = os.path.getsize(path)
        out.append(f"=== {file} (Size: {size} bytes) ===")
        try:
            with open(path, "r", encoding="gbk", errors="ignore") as f:
                lines = [next(f).strip() for _ in range(3)]
                out.extend(lines)
        except Exception as e:
            out.append(f"Error reading: {e}")
        out.append("")

with open(r"D:\GitHub\test\scratch\samples.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
