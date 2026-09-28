#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查拆包后旧函数 API 仍兼容历史单文件备份。"""

import importlib.util
import inspect
import os
import sys
import types

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# V17.2.x(2026-09-10): 原位于 `_obsolete_v17_residue/`（该目录已清理），
# 因本脚本仍以该单文件备份作为比对基准，故将文件本身迁至 `docs/backups/` 长期保留。
BACKUP = os.path.join(ROOT, "docs", "backups", "_sc_datasource_singlefile_backup.py")
sys.path.insert(0, ROOT)

# 1) 载入原单文件备份为独立模块（ground truth）
spec = importlib.util.spec_from_file_location("_sc_ds_backup", BACKUP)
if spec is None or spec.loader is None:
    raise RuntimeError(f"无法加载拆分前备份模块: {BACKUP}")
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)

# 2) 载入新拆包包
import stock_common.sc_datasource as new_pkg  # noqa: E402


def funcs(mod):
    return {n: o for n, o in vars(mod).items() if isinstance(o, types.FunctionType)}


def call_contract(func):
    """Return the runtime call shape, excluding annotations that do not affect calls."""
    signature = inspect.signature(func)
    parameters = [
        parameter.replace(annotation=inspect.Parameter.empty)
        for parameter in signature.parameters.values()
    ]
    return signature.replace(parameters=parameters, return_annotation=inspect.Signature.empty)


bf = funcs(backup)
nf = funcs(new_pkg)

print(f"历史单文件函数数: {len(bf)}")
print(f"当前包导出函数数: {len(nf)}")

missing = set(bf) - set(nf)
extra = set(nf) - set(bf)
print(f"缺失历史函数: {sorted(missing) or '无'}")
print(f"新增函数（信息项）: {len(extra)}")

# 3) 比较调用形态。实现源码和类型注解允许随拆分后的维护演进。
signature_mismatch = []
for name in sorted(set(bf) & set(nf)):
    if call_contract(bf[name]) != call_contract(nf[name]):
        signature_mismatch.append(
            (name, str(call_contract(bf[name])), str(call_contract(nf[name])))
        )

print(f"调用签名检查: {len(set(bf) & set(nf))} 个共同函数，")
print(f"  {'全部兼容 ✅' if not signature_mismatch else str(signature_mismatch)}")

# 4) 模块级状态存在性抽查
state_checks = [
    "_CNINFO_ORGID_CACHE",
    "_PROFIT_FORECAST_CACHE",
    "_EM_L2_MAP",
    "_EM_INDUSTRY_L1_NAMES",
    "_ZHB_REALTIME_FIELDS",
    "_FFLOW_HOSTS",
    "_KPL_HEADERS",
    "_ULIST_BATCH_FIELDS",
    "_EM_BOARD_TYPE_FS_MAP",
    "_calendar_fallback_warned",
    "_TDX_QC_URL",
]
missing_state = [s for s in state_checks if not hasattr(new_pkg, s)]
print(
    f"模块级状态抽查: {len(state_checks)-len(missing_state)}/{len(state_checks)} 存在"
    f"{('；缺失 '+str(missing_state)) if missing_state else ' ✅'}"
)

# 5) 被测试 mock.patch 的关键名字必须存在（保证补丁对内部调用生效）
patched_names = [
    "_em_fflow_request",
    "em_get",
    "get_em_quote_full",
    "get_em_quote_full_delay",
    "start_datacenter_prefetch",
    "get_cyq_distribution",
]
missing_patch = [p for p in patched_names if not hasattr(new_pkg, p)]
print(f"被测补丁目标存在性: {patched_names}")
print(f"  {'全部存在 ✅' if not missing_patch else '缺失 '+str(missing_patch)}")

ok = not missing and not signature_mismatch and not missing_state and not missing_patch
print(
    "\n"
    + (
        "🎉 API 兼容验证通过：历史函数的调用形态、模块状态和 mock 目标均保留。"
        if ok
        else "❌ 验证未通过，见上。"
    )
)
sys.exit(0 if ok else 1)
