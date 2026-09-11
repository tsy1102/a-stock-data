#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V17.2 拆分等价性验证（运行时）：新包 vs 原单文件备份。"""
import importlib.util
import inspect
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# V17.2.x(2026-09-10): 原位于 `_obsolete_v17_residue/`（该目录已清理），
# 因本脚本仍以该单文件备份作为比对基准，故将文件本身迁至 `docs/backups/` 长期保留。
BACKUP = os.path.join(ROOT, "docs", "backups", "_sc_datasource_singlefile_backup.py")
sys.path.insert(0, ROOT)

# 1) 载入原单文件备份为独立模块（ground truth）
spec = importlib.util.spec_from_file_location("_sc_ds_backup", BACKUP)
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)

# 2) 载入新拆包包
import stock_common.sc_datasource as new_pkg  # noqa: E402

def funcs(mod):
    return {n: o for n, o in vars(mod).items() if isinstance(o, types.FunctionType)}

bf = funcs(backup)
nf = funcs(new_pkg)

print(f"备份单文件函数数: {len(bf)}")
print(f"新包函数数:       {len(nf)}")

missing = set(bf) - set(nf)
extra = set(nf) - set(bf)
print(f"新包缺失函数: {sorted(missing) or '无'}")
print(f"新包多出函数: {sorted(extra) or '无'}")

# 3) 逐函数源码字节级比对
mismatch = []
for name in sorted(set(bf) & set(nf)):
    try:
        sb = inspect.getsource(bf[name])
        sn = inspect.getsource(nf[name])
    except (OSError, TypeError) as e:
        mismatch.append((name, f"getsource 失败: {e}"))
        continue
    if sb.strip() != sn.strip():
        mismatch.append((name, "源码不一致"))

print(f"源码逐函数比对: {len(set(bf)&set(nf))} 个函数检查，"
      f"{'全部一致 ✅' if not mismatch else str(mismatch)}")

# 4) 模块级状态存在性抽查
state_checks = ["_CNINFO_ORGID_CACHE", "_PROFIT_FORECAST_CACHE", "_EM_L2_MAP",
                "_EM_INDUSTRY_L1_NAMES", "_ZHB_REALTIME_FIELDS", "_FFLOW_HOSTS",
                "_KPL_HEADERS", "_ULIST_BATCH_FIELDS", "_EM_BOARD_TYPE_FS_MAP",
                "_calendar_fallback_warned", "_TDX_QC_URL"]
missing_state = [s for s in state_checks if not hasattr(new_pkg, s)]
print(f"模块级状态抽查: {len(state_checks)-len(missing_state)}/{len(state_checks)} 存在"
      f"{('；缺失 '+str(missing_state)) if missing_state else ' ✅'}")

# 5) 被测试 mock.patch 的关键名字必须存在（保证补丁对内部调用生效）
patched_names = ["_em_fflow_request", "em_get", "get_em_quote_full",
                 "get_em_quote_full_delay", "start_datacenter_prefetch",
                 "get_cyq_distribution"]
missing_patch = [p for p in patched_names if not hasattr(new_pkg, p)]
print(f"被测补丁目标存在性: {patched_names}")
print(f"  {'全部存在 ✅' if not missing_patch else '缺失 '+str(missing_patch)}")

ok = (not missing and not extra and not mismatch and not missing_state and not missing_patch)
print("\n" + ("🎉 等价性验证通过：新包与原单文件函数/状态完全一致，且无多余/缺失。"
       if ok else "❌ 验证未通过，见上。"))
sys.exit(0 if ok else 1)
