# -*- coding: utf-8 -*-
"""V17.2.x 治理第二批：语义统一（去重下沉 + 限流表不合并说明 + 残留注释）"""
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


# ============ 1) _industry.py 新增共享实现 ============
p = pathlib.Path("stock_common/sc_datasource/_industry.py")
t = p.read_text(encoding="utf-8")
anchor = "def get_industry_comparison(top_n: int = 20) -> Dict[str, Any]:"
assert t.count(anchor) == 1
NEW_FN = '''def get_industry_ranking(top_n: int = 20, _tag: str = "report") -> List[Dict[str, Any]]:
    """V17.2.x(2026-09-10): 行业排名（**list 返回**）——由 val/lng 本地 `industry_comparison` 下沉合并。

    ⚠️ 与相邻 `get_industry_comparison`（**dict 返回**，med 使用）**语义不同，勿混用**：
      - 本函数: 返回 `list[dict]`——ZHB 行业榜行 或 TDX `board_list` 板块（供逐行渲染）；
      - get_industry_comparison: 返回 `{"top"/"bottom"/"all"/"total"}` 聚合结构。
      二者同名近义是历史演化产物，本函数以 `_ranking` 后缀显式区分。

    Args:
        top_n: 返回行业数量上限。
        _tag: 调用方标识（仅用于日志定位，如 "val"/"lng"）。

    Returns:
        list[dict]: 行业行；全部失败时返回 []。
    """
    try:
        rows = get_industry_rank_from_zhb(top_n)
        if rows:
            return rows
    except Exception as _e:
        _debug_log(f"{_tag} industry_rank zhb error: {_e}")
    try:
        # 惰性导入：core↔stock_common 存在循环依赖，沿用项目既有 lazy import 断环手法
        from core.tdx_client import tdx_get_board_list

        sectors = tdx_get_board_list(0)
        if not sectors:
            return []
        return sectors
    except Exception as _e:
        _debug_log(f"{_tag} industry_rank tdx fallback error: {_e}")
        return []


'''
t = t.replace(anchor, NEW_FN + anchor, 1)
p.write_text(t, encoding="utf-8")
print("OK stock_common/sc_datasource/_industry.py: 1 处(新增 get_industry_ranking)")

# ============ 2) val: 删除本地 industry_comparison，改用共享实现 ============
edit("get_val_report.py", [
    ('''def industry_comparison(top_n=20):
    """2026-08-11: 升级 O25——ZHB 快照聚合优先（同 lng/sht/med），TDX board_list 兜底。
    原 V4 直连 TDX board_list：T-1 口径缺失、无市值加权；O25 返回 leader_name 键（老消费方读 leader，兼容处理）。"""
    try:
        from stock_common.sc_datasource import get_industry_rank_from_zhb

        rows = get_industry_rank_from_zhb(top_n)
        if rows:
            return rows
    except Exception as _e:
        _debug_log(f"val industry_rank zhb error: {_e}")
    sectors = tdx_get_board_list(0)
    if not sectors:
        return []
    return sectors''',
     '''def industry_comparison(top_n=20):
    """V17.2.x(2026-09-10): 已下沉至 `stock_common.sc_datasource.get_industry_ranking`，此处仅薄转发。

    保留本名是为兼容既有调用点；实现见共享层（val/lng 原两份近乎重复的实现已合并）。
    返回 list[dict]（ZHB 行业榜行 或 TDX board_list 板块）。
    """
    from stock_common.sc_datasource import get_industry_ranking

    return get_industry_ranking(top_n, "val")'''),
])

# ============ 3) lng: 同上 ============
edit("get_lng_report.py", [
    ('''def industry_comparison(top_n=20):
    """V16.3 O25: 行业排名 → ZHB 本地聚合优先（参照系 T-1 可接受，零网络），
    TDX board_list 兜底（原 V4 直接东财 clist——每次现取，用户纠正应 ZHB）。"""
    try:
        from stock_common.sc_datasource import get_industry_rank_from_zhb

        rows = get_industry_rank_from_zhb(top_n)
        if rows:
            return rows
    except Exception as _e:
        _debug_log(f"lng industry_rank zhb error: {_e}")
    sectors = tdx_get_board_list(0)
    if not sectors:
        return []
    return sectors''',
     '''def industry_comparison(top_n=20):
    """V17.2.x(2026-09-10): 已下沉至 `stock_common.sc_datasource.get_industry_ranking`，此处仅薄转发。

    保留本名是为兼容既有调用点；实现见共享层（lng/val 原两份近乎重复的实现已合并）。
    返回 list[dict]（ZHB 行业榜行 或 TDX board_list 板块）。
    """
    from stock_common.sc_datasource import get_industry_ranking

    return get_industry_ranking(top_n, "lng")'''),
])

# ============ 4) _is_a_stock: val/mak 删除本地包装，直接调 sc_utils ============
edit("get_val_report.py", [(
    '''def _is_a_stock(code: str) -> bool:
    """V17.0 S3: 统一走 sc_utils.is_a_stock（原本地 _A_STOCK_PREFIXES 定义已收敛）。"""
    from stock_common.sc_utils import is_a_stock as _u_is_a_stock

    return _u_is_a_stock(code)''',
    '''def _is_a_stock(code: str) -> bool:
    """V17.2.x(2026-09-10): 直接转调 sc_utils.is_a_stock（原本地前缀表早已收敛）。

    与 mak 的同名包装曾构成两份重复实现，现两者均为同构单行转发，保留仅为调用点兼容。
    """
    from stock_common.sc_utils import is_a_stock

    return is_a_stock(code)''')])

edit("get_mak_report.py", [(
    '''def _is_a_stock(code: str) -> bool:
    """V17.0 S3: 统一走 sc_utils.is_a_stock（原本地 _A_STOCK_PREFIXES 定义已收敛）。"""
    from stock_common.sc_utils import is_a_stock as _u_is_a_stock

    return _u_is_a_stock(code)''',
    '''def _is_a_stock(code: str) -> bool:
    """V17.2.x(2026-09-10): 直接转调 sc_utils.is_a_stock（与 val 同口径：00/30/60/68/92 前缀）。"""
    from stock_common.sc_utils import is_a_stock

    return is_a_stock(code)''')])

# ============ 5) Q5: 限流表不合并 —— 两侧加同步说明 ============
edit("core/tdx_client.py", [(
    "_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {",
    '''# ⚠️ V17.2.x(2026-09-10) 治理说明：本表与 `stock_common/sc_network.py::_DOMAIN_LIMITS` (37 域)
# **有意保持独立、不合并**（用户决策 Q5），原因：
#   - 本表服务于 **TDX TCP 长连接**（easy_tdx，连接复用、按"连接级"节流）；
#   - sc_network 表服务于 **HTTP 请求级**节流（每次请求独立限流 + 429 退避）；
#   - 二者语义不同（长连接节流 vs 请求节流），强行统一会导致 TDX 侧被 HTTP 的严格 rps 误伤，
#     或 HTTP 侧失去 TDX 的连接复用保护。
#   本表 6 域是 sc_network 37 域的子集；**新增/调整域名时须两处同步评估**。
_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {''')])

edit("stock_common/sc_network.py", [(
    "_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {",
    '''# ⚠️ V17.2.x(2026-09-10) 治理说明：本表与 `core/tdx_client.py::_DOMAIN_LIMITS` (6 域)
# **有意保持独立、不合并**（用户决策 Q5）——本表为 **HTTP 请求级**节流，
# tdx_client 表为 **TDX TCP 长连接级**节流，语义不同不可统一。
#   本表 37 域覆盖 HTTP 数据源；tdx_client 的 6 域是其子集（走 TCP 通道）。
#   **新增/调整域名时须两处同步评估**（详见 tdx_client 侧同名说明）。
_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {''')])

# ============ 6) README:10 移除 thsdk 历史表述 ============
edit("README.md", [(
    "- **多源字段逆向破解**：ZHB / TDX 0x0010 / 东财 push2 / 腾讯 / 新浪 / 同花顺 fuyao·thsdk / 巨潮 / FTShare 私有协议字段交叉验证",
    "- **多源字段逆向破解**：ZHB / TDX 0x0010 / 东财 push2 / 腾讯 / 新浪 / 同花顺 fuyao / 巨潮 / FTShare 私有协议字段交叉验证（thsdk 通道已于 V17.0.29 移除）")])

print("BATCH2_ALL_DONE")
