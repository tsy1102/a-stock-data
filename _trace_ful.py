import faulthandler, time

# 90秒后 dump 所有线程堆栈（含卡死位置）
faulthandler.dump_traceback_later(90, exit=True)

import get_ful_report as g

print("=== 调用 analyze_stock('000100') 完整流程 ===", flush=True)
t0 = time.time()
try:
    name, report = g.analyze_stock("000100", parallel=True)
    print(f"=== analyze_stock 返回 (用时 {time.time()-t0:.1f}s) ===", flush=True)
    print(f"name={name}, report_len={len(report)}", flush=True)
except Exception as e:
    print(f"=== analyze_stock 抛异常: {type(e).__name__}: {e} ===", flush=True)
