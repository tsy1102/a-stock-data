"""
(A) 从最新 raw_ulist239.json 提取 000568 的 f161-f210 裸值(碰撞靶标)
(B) CDP 自驱抓取 data.eastmoney.com/zjlx/000568.html 多周期资金流向, 与 (A) 碰撞
"""

import sys, os, json, glob, time, urllib.request, websocket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cdp_scrape as C

OUT = os.path.dirname(os.path.abspath(__file__)) + "/raw"


# ---------- (A) 提取靶标 ----------
def latest_raw():
    files = glob.glob(
        r"C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/2026*/raw_ulist239.json"
    )
    files += glob.glob(
        r"C:/Tencent/WorkBuddy/a-stock-data/docs/field_verification/2026*/raw_ulist239.json"
    )
    # 按 mtime 取最新
    files = sorted(set(files), key=lambda p: os.path.getmtime(p))
    return files[-1] if files else None


raw_path = latest_raw()
print("RAW:", raw_path)
data = json.load(open(raw_path, encoding="utf-8"))
# 找 000568
entry = None
if isinstance(data, dict):
    for k, v in data.items():
        if "000568" in str(k):
            entry = v
            break
    if entry is None and "items" in data:
        data = data["items"]
if isinstance(data, list):
    for it in data:
        if str(it.get("code", "")) == "000568" or "000568" in str(it.get("CODE", "")):
            entry = it
            break
print("ENTRY keys sample:", list(entry.keys())[:10] if entry else None)
targets = {}
for i in range(161, 211):
    fk = f"f{i}"
    if entry and fk in entry:
        targets[fk] = entry[fk]
print("\n===== 000568 f161-f210 裸值 =====")
for i in range(161, 211):
    fk = f"f{i}"
    print(f"{fk} = {targets.get(fk, '<MISS>')}")

# ---------- (B) 抓取 zjlx 多周期 ----------
print("\n\n===== CDP 抓取 zjlx 000568 =====")
zurl = "https://data.eastmoney.com/zjlx/000568.html"
try:
    b, tid, ws = C.new_tab(zurl)
    time.sleep(12)
    txt0 = C.get_text(ws) or ""
    open(f"{OUT}/zjlx_000568_今日.txt", "w", encoding="utf-8").write(txt0)
    print(f"  今日 text_len={len(txt0)}")
    # 多周期标签
    for period in ["3日", "5日", "10日", "20日", "近3日", "近5日", "近10日", "近20日"]:
        r = C.click_by_text(ws, period)
        time.sleep(5)
        txt = C.get_text(ws) or ""
        open(f"{OUT}/zjlx_000568_{period}.txt", "w", encoding="utf-8").write(txt)
        print(f"  click {period} -> {r} text_len={len(txt)}")
    ws.close()
    b.close()
except Exception as e:
    print("  zjlx ERR", repr(e))
print("\nDONE")
