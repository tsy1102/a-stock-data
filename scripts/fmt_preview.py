# -*- coding: utf-8 -*-
"""fmt_preview.py — 格式调整离线预览工具(零网络).

用途: 调整 5 大脚本 md 生成格式时, 不联网验证排版效果,
避免频繁实跑触发东财 IP 风控。

用法:
  python scripts/fmt_preview.py                # 重转 reports 最新报告(md_render 效果)
  python scripts/fmt_preview.py <file.md>      # 重转指定报告文件
  python scripts/fmt_preview.py --lines "行1;行2;..."   # 直接喂模拟脚本输出行
  python scripts/fmt_preview.py --file xxx.py --range 1200-1250  # 提取脚本某段 L() 输出模拟

输出: C:\\Opencode\\reports\\_preview_out.md(可反复覆盖)
"""
import sys, io, os, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_common.md_render import text_to_md

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "_preview_out.md")


def preview_lines(lines):
    md = text_to_md(lines)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"预览已写入: {OUT} ({len(md)} 行)")
    for ln in md[:60]:
        print(ln)


def preview_file(path):
    raw = open(path, encoding="utf-8").read().splitlines()
    print(f"输入: {path} ({len(raw)} 行) — 二次转换预览(仅测 md_render 新规则)")
    preview_lines(raw)


def extract_script_lines(path, range_str):
    """从脚本提取 L() 输出行(模拟运行)——匹配 L("...")/L(f"...") 字面量."""
    src = open(path, encoding="utf-8").read()
    a, b = (int(x) for x in range_str.split("-"))
    lines = src.splitlines()[a - 1:b]
    out = []
    for ln in lines:
        m = re.search(r'L\((f?)"((?:[^"\\]|\\.)*)"\)', ln)
        if m:
            val = m.group(2).encode().decode("unicode_escape") if False else m.group(2)
            out.append(val.replace("\\n", "\n"))
        else:
            out.append(ln.strip())
    print(f"提取 {path} L{a}-{b} 共 {len(out)} 行(模拟输出)")
    preview_lines(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        fs = sorted(x for x in os.listdir(d) if x.endswith(".md") and not x.startswith("_"))
        if fs:
            preview_file(os.path.join(d, fs[-1]))
        else:
            print("reports 无报告文件")
    elif args[0] == "--lines":
        preview_lines([s.strip() for s in args[1].split(";")])
    elif args[0] == "--file" and len(args) >= 4 and args[2] == "--range":
        extract_script_lines(args[1], args[3])
    else:
        preview_file(args[0])
