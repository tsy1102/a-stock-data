import time
from stock_common.f10_parser import parse_paragraph_blocks, MAX_PARSE_LINES

print(f"MAX_PARSE_LINES={MAX_PARSE_LINES}")

# 构造超大输入（50万行，模拟异常大 F10 文本）
big = ("2026-06-21 15:31│某标题文字内容\n") * 500000
t0 = time.time()
try:
    r = parse_paragraph_blocks(big)
    print(f"500k lines -> {len(r)} blocks in {time.time()-t0:.2f}s")
except Exception as e:
    print(f"ERR {type(e).__name__}: {e} ({time.time()-t0:.2f}s)")

# 测试可能触发回溯的变态行
weird = "x" * 20000 + "2026-06-21 15:31│标题" + "y" * 20000
t0 = time.time()
try:
    r = parse_paragraph_blocks(weird)
    print(f"weird line -> {len(r)} blocks in {time.time()-t0:.2f}s")
except Exception as e:
    print(f"ERR {type(e).__name__}: {e} ({time.time()-t0:.2f}s)")
