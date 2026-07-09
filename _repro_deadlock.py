import threading, time, sys
import faulthandler
faulthandler.dump_traceback_later(40, exit=True)

# 两个线程同时触发 @cached 写 SQLite，模拟 batch2 的 lng+ful 并发写
from stock_common.sc_datasource import get_strategic_announcements, get_concept_blocks

def worker(wid):
    print(f"[w{wid}] start", flush=True)
    t0 = time.time()
    try:
        # 这两个函数都有 @cached，会写 stock_cache.db
        get_strategic_announcements("000100", page_size=10, days=30)
        get_concept_blocks("000100")
        print(f"[w{wid}] done in {time.time()-t0:.1f}s", flush=True)
    except Exception as e:
        print(f"[w{wid}] ERR {type(e).__name__}: {e}", flush=True)

ts = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
for t in ts: t.start()
for t in ts: t.join(timeout=35)
print("ALL DONE" if all(not t.is_alive() for t in ts) else "DEADLOCK/STILL RUNNING")
