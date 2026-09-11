# -*- coding: utf-8 -*-
"""V17.2.x 治理第一批：P0 资金流口径统一 + 文档订正"""
import pathlib


def edit(path, pairs):
    p = pathlib.Path(path)
    t = p.read_text(encoding="utf-8")
    for i, (old, new) in enumerate(pairs):
        assert old in t, f"[{path}] 第{i+1}处未匹配:\n{old[:200]}"
        assert t.count(old) == 1, f"[{path}] 第{i+1}处非唯一({t.count(old)})"
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print(f"OK {path}: {len(pairs)} 处")


# ============ P0: 统一 get_fund_flow_120d 口径 ============
edit("get_sht_report.py", [(
    '''def get_fund_flow_120d(code):
    """V16.2.4 (D2): 统一走 sc_datasource.get_history_fund_flow_120d（TDX 优先→东财 fallback）。

    V7.5 原实现：TDX TCP + 东财 push2his fallback；统一后 em fallback 走 get_em_history_fund_flow
    （dict 列表，元），sht 侧 _is_dict 分支天然兼容。
    """
    from stock_common import get_history_fund_flow_120d
    return get_history_fund_flow_120d(code, 60, prefer="tdx")''',
    '''def get_fund_flow_120d(code):
    """V17.2.x(2026-09-10) 统一口径：与 med 对齐为 `prefer="em"`（东财直连）。

    ⚠️ 变更依据（非行为变更，数据完全等价）：
      - 原 sht 用 `prefer="tdx"`、med 用 `prefer="em"`，看似两口径；
      - 实测 `tdx_get_history_fund_flow`(`core/tdx_client.py:1694`) **已完全委托东财 HTTP**
        （"V12.0: 委托到东财 HTTP 接口（原 TDX get_history_fund_flow 已废弃）"），
        且 V17.0.13 口径规定主力净额统一走东财 push2 f137+f140 —— **两路径数据同源同值**；
      - `prefer="tdx"` 仅多一次对同一函数的冗余二次调用，且会把 `source` 误标为 "tdx"。
      故统一为 "em" 直连：数据不变、source 标注正确、少一层间接调用。
    """
    from stock_common import get_history_fund_flow_120d
    return get_history_fund_flow_120d(code, 60, prefer="em")''')])

edit("get_med_report.py", [(
    '''def get_fund_flow_120d(code):
    """V16.2.4 (D2): 统一走 sc_datasource.get_history_fund_flow_120d（东财直连）。

    V7.5 原实现直连 get_em_history_fund_flow；统一后保留"仅东财"口径（中线业绩视角）。
    """
    from stock_common import get_history_fund_flow_120d
    return get_history_fund_flow_120d(code, 60, prefer="em")''',
    '''def get_fund_flow_120d(code):
    """V17.2.x(2026-09-10) 统一口径：sht 已对齐至本 `prefer="em"`（东财直连）。

    原注释称"保留仅东财口径（中线业绩视角）"以区别于 sht 的 TDX 优先——该区分已不成立：
    `tdx_get_history_fund_flow` 自 V12.0 起即委托东财 HTTP，两路径数据同源同值。
    现 med 与 sht 完全一致（同一函数、同一参数），跨报告资金流结论可直接横向比较。
    """
    from stock_common import get_history_fund_flow_120d
    return get_history_fund_flow_120d(code, 60, prefer="em")''')])

# 同步更新统一入口 docstring，标注 prefer="tdx" 为历史别名
edit("stock_common/sc_datasource/_eastmoney.py", [(
    '''        prefer: "tdx"=TDX 优先→东财 fallback（sht 短线口径）；
                "em"=仅东财（med 中线口径）；"auto"=TDX 优先''',
    '''        prefer: "em"=东财直连（**推荐且为 sht/med 统一口径，2026-09-10 起**）；
                "tdx"=⚠️ 历史别名，勿再用：其调用的 tdx_get_history_fund_flow
                      自 V12.0 起已完全委托东财 HTTP，与本值同源同值，
                      却会多一次冗余二次调用并把 source 误标为 "tdx"；
                "auto"=同 "tdx"（保留仅为向后兼容）''')])

# ============ P1: 移除 thsdk 表述（V17.0.29 已删除该模块） ============
edit("README.md", [
    (
        "2. `pip install -r requirements.txt`（运行时依赖 17+ 项；`levistock/axdata/thsdk` 为可选增强，缺失自动降级）",
        "2. `pip install -r requirements.txt`（运行时依赖 16 项；`levistock`/`axdata` 为可选增强，缺失自动降级）\n"
        "   > ⚠️ **`thsdk` 已于 V17.0.29(2026-09-07) 随 `stock_common/sc_ths.py` 一同移除**，不再是可选依赖。",
    ),
    (
        "运行时依赖见 [`requirements.txt`](requirements.txt)（17+ 项；`levistock`/`axdata`/`thsdk` 可选，缺失自动降级）",
        "运行时依赖见 [`requirements.txt`](requirements.txt)（16 项；`levistock`/`axdata` 可选，缺失自动降级）",
    ),
    # P3: 数字订正
    (
        "- **`stock_common/sc_network.py`**：分域限流（38 域）、进程文件锁、429 退避、连续封禁 20h 冷却。",
        "- **`stock_common/sc_network.py`**：分域限流（37 域）、进程文件锁、429 退避、连续封禁 20h 冷却。\n"
        "  > 注：`core/tdx_client.py::_DOMAIN_LIMITS` 另有 6 域**独立**限流表（TCP 长连接语义，与 HTTP 请求级节流不同，**有意不合并**）。",
    ),
    (
        "│   ├── sc_datasource.py          # 数据源查询模块（100+ 函数）",
        "│   ├── sc_datasource/            # 数据源查询包（8 个子模块，138 个函数）",
    ),
])

# requirements.txt: thsdk 注释块更新
edit("requirements.txt", [(
    '''# ── V16.3 O30 新数据源（可选，缺失时 THS 增强自动降级）──────────────
# thsdk: 同花顺官方 C 库 SDK（sc_ths.py 依赖；正式账号见 ths_credentials.json，
#        缺失时 get_ths_market_snapshot / get_ths_pb 等返回空/None）
#
# ⚠️⚠️ 包名撞车警告（2026-09-06 实测，勿再踩）：
#   PyPI 上的 `thsdk`（2.0.2，summary="Python SDK for financial market data"）是**同名不同库**，
#   它**不导出 `THS` 类**；本项目 `stock_common/sc_ths.py:63` 需要的是 `from thsdk import THS`
#   （同花顺官方 C 库 SDK，非 PyPI 公开分发，需从官方渠道获取 wheel 后本地安装）。
#   装上 PyPI 版本只会把报错从 "No module named 'thsdk'" 变成
#   "cannot import name 'THS' from 'thsdk'"，并让 pip 误报依赖已满足 —— 已在 2026-09-06 卸载。
#   正确做法：拿到官方 wheel 后 `pip install <path-to-wheel>`，勿用 `pip install thsdk`。
# 缺失属预期：相关功能自动降级，不影响主流程与回归（526 passed）。
# thsdk>=0.1    ← 有意保留为注释：标记该依赖真实不可从 PyPI 满足''',
    '''# ── thsdk（同花顺官方 C 库 SDK）—— V17.0.29(2026-09-07) 已完全移除 ──────────
# ❌ 本依赖**不再是可选增强**，`stock_common/sc_ths.py` 已删除，请勿再安装或寻找。
#    移除原因：thsdk TCP 网关仅盘中可用，对盘后/盘前运行无价值（详见 CHANGELOG V17.0.29）。
#    现行替代：主力净流入走东财 push2 f137；PB 由 TDX `price/bvps` 兜底；
#              保留同花顺 HTTP 网页接口（强势股热榜 / 涨停揭秘，盘后仍可用）。
#
# 📌 历史包名撞车记录（2026-09-06 实测，留档以防回退时重踩）：
#   PyPI 上的 `thsdk`（2.0.2）是**同名不同库**，不导出 `THS` 类；
#   装上只会把报错从 "No module named 'thsdk'" 变成 "cannot import name 'THS'"，
#   并让 pip 误报依赖已满足。即便未来要恢复，也应 `pip install <官方 wheel>` 而非 PyPI 包。''')])

print("BATCH1_ALL_DONE")
