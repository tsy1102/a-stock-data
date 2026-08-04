import sys
with open(r"D:\GitHub\test\scratch\zhb_20260713\tipinfo.dat", "r", encoding="gbk", errors="ignore") as f:
    for line in f:
        if "600519" in line:
            print("600519 tipinfo:", line.strip())
        if "000001" in line:
            print("000001 tipinfo:", line.strip())
        if "300750" in line:
            print("300750 tipinfo:", line.strip())
