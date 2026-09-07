# -*- coding: utf-8 -*-
"""对 5 个 Runner 的 execute_pipeline 注入 4 处回归，验证新测试是否真能捕获。

每处注入后跑对应测试文件，看目标用例是否失败；随后立即 `git checkout` 还原。
被测文件在 git 中未修改，可安全用 checkout 还原。
"""
import io
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = r"C:\Tencent\WorkBuddy\a-stock-data"
PY = r"C:\Users\tsy11\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe"
TESTFILE = "tests/reports/test_reports_pipeline.py"

MUTATIONS = [
    {
        "name": "① sht 行业对比缓存未注入 gen_kwargs（退化成逐股重拉）",
        "file": "get_sht_report.py",
        "old": '"ind_comp": _cached_ind_comp, "idx_q": _cached_idx_q,',
        "new": '"ind_comp": None, "idx_q": _cached_idx_q,',
        "expect": "test_industry_comparison_injected_into_gen_kwargs",
    },
    {
        "name": "② sht depth 席位开关失效（永远关席位）",
        "file": "get_sht_report.py",
        "old": "_seats_on = _depth != \"lite\"",
        "new": "_seats_on = False  # MUTATION",
        "expect": "test_depth_deep_enables_seats",
    },
    {
        "name": "③ val 去掉「异步失败→同步回退」",
        "file": "get_val_report.py",
        "old": "                run_discovery(op)",
        "new": "                raise  # MUTATION: 去掉同步回退",
        "expect": "test_falls_back_to_sync_when_async_fails",
    },
    {
        "name": "④ val 去掉 O39 假成功守卫（无条件报已保存）",
        "file": "get_val_report.py",
        "old": "            if os.path.exists(op):",
        "new": "            if True:  # MUTATION: 去掉文件存在性校验",
        "expect": "test_no_false_success_when_file_missing",
    },
]


def run_tests():
    r = subprocess.run(
        [PY, "-m", "pytest", TESTFILE, "-p", "no:cacheprovider",
         "-q", "--tb=no", "-rf"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    return r.stdout + r.stderr, r.returncode


results = []
for m in MUTATIONS:
    path = os.path.join(ROOT, m["file"])
    src = io.open(path, encoding="utf-8", newline="").read()
    if m["old"] not in src:
        results.append((m["name"], "跳过（锚点未找到，源码可能已变更）", False))
        continue
    io.open(path, "w", encoding="utf-8", newline="").write(
        src.replace(m["old"], m["new"], 1))

    out, code = run_tests()
    failed = m["expect"] in out and ("FAILED" in out or "failed" in out)
    # 精确判定：目标用例出现在失败清单里
    hit = False
    for line in out.splitlines():
        if line.startswith("FAILED") and m["expect"] in line:
            hit = True
            break
    results.append((m["name"], ("被捕获 ✅" if hit else "未捕获 ❌"), hit))

    subprocess.run(["git", "checkout", "--", m["file"]], cwd=ROOT,
                   capture_output=True)

print("=" * 74)
print("变异测试（注入回归 → 看新测试能否抓住）")
print("=" * 74)
for name, verdict, ok in results:
    print(f"  {name}")
    print(f"      → {verdict}")
    print()

caught = sum(1 for _n, _v, ok in results if ok)
total = sum(1 for _n, v, _ok in results if "跳过" not in v)
print("=" * 74)
print(f"结果：{caught}/{total} 被捕获")
print("=" * 74)

# 确认已全部还原
r = subprocess.run(["git", "status", "--short"], cwd=ROOT,
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
dirty = [l for l in r.stdout.splitlines()
         if "get_sht_report.py" in l or "get_val_report.py" in l]
print("被测文件残留改动:", dirty if dirty else "无（已全部还原）")
