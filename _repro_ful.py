import threading, time, requests
from stock_common import UA, _quick_request

TARGETS = [
    ("np-weblist", "https://np-weblist.eastmoney.com/comm/web/getFastNewsList?client=web&biz=web_724&fastColumn=102&pageSize=3"),
    ("cninfo_orgid", "https://www.cninfo.com.cn/new/data/szse_stock.json"),
    ("cninfo_ann", "https://www.cninfo.com.cn/new/hisAnnouncement/query"),
]

def worker(wid):
    for i in range(8):
        for name, url in TARGETS:
            try:
                r = requests.get(url, headers={"User-Agent": UA}, timeout=10)
                print(f"  [w{wid}] {name} -> {r.status_code}")
            except Exception as e:
                print(f"  [w{wid}] {name} -> ERR {type(e).__name__}")

print("=== Phase 1: 3 threads x 8 rounds concurrent load ===")
ts = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
t0 = time.time()
for t in ts: t.start()
for t in ts: t.join(timeout=120)
print(f"Phase1 done in {time.time()-t0:.1f}s")

print("\n=== Phase 2: simulate layer_risk single call (should NOT hang) ===")
t0 = time.time()
try:
    r = requests.get("https://np-weblist.eastmoney.com/comm/web/getFastNewsList?client=web&biz=web_724&fastColumn=102&pageSize=3",
                     headers={"User-Agent": UA}, timeout=10)
    print(f"  layer_risk call -> {r.status_code} ({time.time()-t0:.1f}s)")
except Exception as e:
    print(f"  layer_risk call -> ERR {type(e).__name__} ({time.time()-t0:.1f}s)")
print("DONE")
