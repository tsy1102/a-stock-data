# 该脚本被并发启动多次，模拟 main.py 的多个子进程同时写 cache DB
import sys, time
from stock_common.sc_datasource import get_strategic_announcements
code = sys.argv[1] if len(sys.argv) > 1 else "000100"
t0 = time.time()
get_strategic_announcements(code, page_size=10, days=30)
print(f"PID={__import__('os').getpid()} done {time.time()-t0:.1f}s", flush=True)
