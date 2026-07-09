import time, sys
from stock_common.f10_parser import parse_paragraph_blocks, MAX_PARSE_LINES

with open("_parse_result.txt", "w", encoding="utf-8") as f:
    f.write(f"MAX_PARSE_LINES={MAX_PARSE_LINES}\n")
    f.flush()

    # 小输入
    t0 = time.time()
    r = parse_paragraph_blocks("2026-06-21 15:31|x\n2026-06-21 15:31|y\n")
    f.write(f"small -> {len(r)} in {time.time()-t0:.3f}s\n")
    f.flush()

    # 超大输入
    big = ("2026-06-21 15:31|title\n") * 500000
    t0 = time.time()
    r = parse_paragraph_blocks(big)
    f.write(f"big -> {len(r)} blocks in {time.time()-t0:.3f}s\n")
    f.flush()
    f.write("DONE\n")
