"""_industry.py — V17.2 拆包子模块（共享命名空间片段，由 __init__ 载入）

本文件现为独立可导入子模块（不再经 exec 注入）。
由 stock_common/sc_datasource/__init__.py 通过  显式 re-export 到包命名空间；
跨片段符号由各子模块函数体内的局部懒导入（from ._DEFINER import NAME）提供，
共享可变状态集中于 _shared.py（单实例）。
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import asyncio
import code
import os
import stat
from stock_common.sc_network import UA, _debug_log, em_get, requires_push2
from stock_common.sc_utils import _load_strategy_config, _safe_float, em_secid_prefix
from core.stock_cache import TTL, cached, make_valid_if
from ._shared import _EM_BOARD_TYPE_FS_MAP, _EM_INDUSTRY_L1_NAMES, _EM_L2_LOADED_TS, _EM_L2_MAP, _EM_L2_MEMBERS, _EM_L2_TTL, _TDXHY_CACHE
from stock_common.sc_kpl import _f


@cached(category="industry_reports", ttl_seconds=TTL["reports"])
def get_industry_reports(
    industry_code: str = "*", max_pages: int = 3, begin_time: str = "2024-01-01"
) -> List[Dict[str, Any]]:
    """东财行业研报列表查询（SKILL.md V3.2.3 新增，qType=1）。

    与个股研报同一端点，仅 qType 参数不同：
    - qType=0: 个股研报（get_reports）
    - qType=1: 行业研报（本函数）

    Args:
        industry_code: 东财行业代码，"*"表示全行业
        max_pages: 最大页数（每页100条）
        begin_time: 起始日期（格式：YYYY-MM-DD）

    Returns:
        list: 行业研报记录列表，包含行业名称、评级、报告类型等字段

    行业研报特有字段：
        - industryName: 行业名称（如 IT服务Ⅱ、风电设备、光伏设备）
        - industryCode: 东财行业代码（用于精确过滤）
        - emRatingName: 行业评级（买入/增持/中性/...）
        - reportType: 报告类型
        - infoCode: 用于拼接PDF下载URL
    """
    api_url = "https://reportapi.eastmoney.com/report/list"
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "industryCode": industry_code,
            "pageSize": "100",
            "industry": "*",
            "rating": "*",
            "beginTime": begin_time,
            "endTime": "2030-01-01",
            "pageNo": str(page),
            "fields": "",
            "qType": "1",
            "orgCode": "",
            "code": "",
            "rcode": "",
            "p": str(page),
            "pageNum": str(page),
            "pageNumber": str(page),
        }
        try:
            r = em_get(
                api_url,
                params=params,
                headers={"Referer": "https://data.eastmoney.com/"},
                timeout=30,
            )
            if r is None:
                break
            d = r.json()
            rows = d.get("data") or []
            if not rows:
                break
            all_records.extend(rows)
            if page >= (d.get("TotalPage", 1) or 1):
                break
        except Exception as _e:
            _debug_log(f"datasource get_industry_reports page {page} ({industry_code}): {_e}")
            break
    return all_records


@cached(
    category="industry_peers_v2",
    ttl_seconds=TTL["industry_peers_v2"],
    trading_day=True,
    valid_if=lambda r: isinstance(r, dict)
    and bool(r.get("peers"))
    and any(p.get("price", 0) > 0 for p in r["peers"] if isinstance(p, dict)),
)
def get_industry_peers(
    code: str, top_n: int = 3, info: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """V7.5: 同业对比 — TDX 三级兜底（belong_board → board_members → board_by_name）。

    返回: {
        "industry": str, "my_mcap": float, "my_rank": int, "industry_count": int,
        "peers": [...], "all_members": [...]
    }
    """
    from ._quotes import get_tencent_quote
    from core.tdx_client import tdx_get_belong_boards, tdx_get_board_members, tdx_get_board_by_name
    from stock_common.sc_utils import _load_strategy_config

    _sc = _load_strategy_config()
    _mkt_cfg = _sc.get("market", {})
    _peers_low = _mkt_cfg.get("peers_mcap_low", 0.3)
    _peers_high = _mkt_cfg.get("peers_mcap_high", 3.0)

    # 0. V16.2.17: 东财申万二级优先（datacenter 一次性映射缓存，零逐股请求；
    # 成员市值用腾讯批量（进程内按交易日缓存，跨 mak/val/sht 复用））
    try:
        _l2 = get_em_industry_l2(code)
        if _l2:
            _l2_members = get_em_industry_members_l2(_l2)
            if _l2_members:
                from core.tdx_client import _tencent_batch_fallback

                _tq = _tencent_batch_fallback(_l2_members) or {}
                _rows = []
                for _mc in _l2_members:
                    # 过滤 B 股（200xxx/900xxx）与非 A 股代码，避免排行污染
                    if len(_mc) != 6 or not _mc.isdigit() or _mc[:2] not in ("00", "30", "60", "68", "92"):
                        continue
                    _q = _tq.get(_mc) or {}
                    _rows.append(
                        {
                            "code": _mc,
                            "name": _q.get("name", _mc),
                            "price": _q.get("price", 0) or 0,
                            "change_pct": _q.get("change_pct", 0) or 0,
                            "mcap_yi": _q.get("mcap_yi", 0) or 0,
                            "pe": _q.get("pe_ttm", 0) or 0,
                            # V17.0.23: 静态PE(f163) 横向比较（V17.0.29 清理重复键行）
                            "pe_lyr": _q.get("pe_lyr", 0) or 0,
                            "turnover": _q.get("turnover_pct", 0) or 0,
                        }
                    )
                _by_mcap = sorted(_rows, key=lambda x: x["mcap_yi"], reverse=True)
                _my_mcap = next((r["mcap_yi"] for r in _by_mcap if r["code"] == code), 0)
                _my_rank = next((i for i, r in enumerate(_by_mcap, 1) if r["code"] == code), 0)
                _others = [r for r in _by_mcap if r["code"] != code]
                _peers = []
                if _others:
                    _peers.append(_others[0])  # 行业龙头
                if _my_mcap > 0:
                    _similar = [
                        r
                        for r in _others[1:]
                        if _peers_low * _my_mcap <= r["mcap_yi"] <= _peers_high * _my_mcap
                    ]
                    _peers += _similar[: top_n - 1]
                if len(_peers) < top_n:
                    _peers += [r for r in _others if r not in _peers][: top_n - len(_peers)]
                return {
                    "industry": _l2,
                    "my_mcap": _my_mcap,
                    "my_rank": _my_rank,
                    "industry_count": len(_l2_members),
                    "peers": _peers[:top_n],
                    "all_members": _by_mcap,
                }
    except Exception as _e:
        _debug_log(f"datasource get_industry_peers em_l2 ({code}): {_e}")

    # 1. TDX board_members（通过 belong_board 获取 board_code）
    boards = tdx_get_belong_boards(code)
    industry_boards = boards.get("industry", []) if boards else []

    if industry_boards:
        primary = industry_boards[0]
        members = tdx_get_board_members(primary["code"])
        if not members:
            members = tdx_get_board_by_name(primary["name"], board_type=0)
        if members:
            members_by_mcap = sorted(members, key=lambda x: x.get("mcap_yi", 0), reverse=True)
            my_mcap = 0
            my_rank = 0
            for i, m in enumerate(members_by_mcap, 1):
                if m["code"] == code:
                    my_mcap = m.get("mcap_yi", 0)
                    my_rank = i
                    break
            # 第一只：行业标杆（市值最大），其余：市值相近（0.3~3 倍）
            others = [m for m in members_by_mcap if m["code"] != code]
            peers = []
            if others:
                peers.append(others[0])  # 行业龙头
            if my_mcap > 0:
                similar = [
                    m
                    for m in others[1:]
                    if _peers_low * my_mcap <= m.get("mcap_yi", 0) <= _peers_high * my_mcap
                ]
                peers += similar[: top_n - 1]
            if len(peers) < top_n:
                peers += [m for m in others if m not in peers][: top_n - len(peers)]

            # V8.9: 腾讯行情 fallback — TDX 返回 price=0 时用腾讯补全
            for _p in peers:
                if _p.get("price", 0) <= 0:
                    try:
                        from stock_common import get_tencent_quote

                        _q = get_tencent_quote(_p["code"])
                        if _q and _q.get("price", 0) > 0:
                            _p["price"] = _q.get("price", _p["price"])
                            _p["change_pct"] = _q.get("change_pct", _p["change_pct"])
                            _p["mcap_yi"] = _q.get("mcap_yi", _p["mcap_yi"])
                            _p["pe"] = _q.get("pe_ttm", _p["pe"])
                            _p["pe_lyr"] = _q.get("pe_lyr", _p.get("pe_lyr", 0))
                            _p["turnover"] = _q.get("turnover_pct", _p["turnover"])
                    except Exception as _e:
                        _debug_log(f"datasource tencent quote fallback error: {_e}")

            # V17.0.29 (2026-09-02 P1 修复): 上方 V8.9 兜底只在 price<=0 时触发, 而 TDX
            # board_members 返回的 price 有效 → 该分支永不执行, peers 字典根本没有 pe_lyr 键,
            # 同业对比表 PE（静） 整列 N/A(实测 002193/002360/300165/301171 的 peers pe_lyr 均为 None)。
            # 改为: 对缺失/为 0 的 pe_lyr 用腾讯批量(1 次请求, 进程级按日缓存)补静态PE, 不覆盖已有值。
            _need_lyr = [str(_p.get("code", "")) for _p in peers
                         if str(_p.get("code", "")) and not (_p.get("pe_lyr") or 0)]
            if _need_lyr:
                try:
                    from core.tdx_client import _tencent_batch_fallback

                    _tq = _tencent_batch_fallback(_need_lyr) or {}
                    for _p in peers:
                        _c = str(_p.get("code", ""))
                        _lyr = (_tq.get(_c) or {}).get("pe_lyr")
                        if _lyr:
                            _p["pe_lyr"] = _lyr
                except Exception as _e:
                    _debug_log(f"datasource peers pe_lyr batch fallback error: {_e}")
            return {
                "industry": primary["name"],
                "my_mcap": my_mcap,
                "my_rank": my_rank,
                "industry_count": len(members),
                "peers": peers[:top_n],
                "all_members": members_by_mcap,
            }

    # 2. Fallback: 无 industry_boards → 用 info.industry + board_list 匹配
    ind_name = info.get("industry", "") if info else ""
    if ind_name:
        st = tdx_get_board_by_name(ind_name, board_type=0)
        if st:
            st_by_mcap = sorted(st, key=lambda x: x.get("mcap_yi", 0), reverse=True)
            my_mcap = 0
            my_rank = 0
            for i, s in enumerate(st_by_mcap, 1):
                if s["code"] == code:
                    my_mcap = s.get("mcap_yi", 0)
                    my_rank = i
                    break
            others = [s for s in st_by_mcap if s["code"] != code]
            peers = []
            if others:
                peers.append(others[0])
            if my_mcap > 0:
                similar = [
                    s
                    for s in others[1:]
                    if _peers_low * my_mcap <= s.get("mcap_yi", 0) <= _peers_high * my_mcap
                ]
                peers += similar[: top_n - 1]
            if len(peers) < top_n:
                peers += [s for s in others if s not in peers][: top_n - len(peers)]
            return {
                "industry": ind_name,
                "my_mcap": my_mcap,
                "my_rank": my_rank,
                "industry_count": len(st),
                "peers": peers[:top_n],
            }

    # 3. V9.0 Fallback: F10 行业分析（仅返回行业名 + 公司规模排名，无 peer 市值）
    try:
        from core.tdx_client import tdx_get_industry_analysis

        f10 = tdx_get_industry_analysis(code)
        if f10:
            industry_info = f10.get('industry', {})
            company_scale = f10.get('company_scale', {})
            industry_name = industry_info.get('name', '') if industry_info else ''
            industry_count = industry_info.get('total_count', 0) if industry_info else 0
            my_rank_info = company_scale.get('my_rank', {}) if company_scale else {}
            # 从 my_rank 字典中提取排名（不同字段名兼容）
            my_rank = 0
            if my_rank_info:
                for k, v in my_rank_info.items():
                    if '排名' in k or '名次' in k or k.lower() == 'rank':
                        try:
                            my_rank = int(str(v).replace('第', '').replace('名', '').strip())
                        except (ValueError, TypeError):
                            pass
                        break
            # top_rankings 作为 peers（无市值/价格，仅基本信息）
            top_rankings = company_scale.get('top_rankings', []) if company_scale else []
            peers = []
            for r in top_rankings[:top_n]:
                peers.append(
                    {
                        "code": r.get('代码', r.get('股票代码', '')),
                        "name": r.get('名称', r.get('股票简称', '')),
                        "price": 0,
                        "change_pct": 0,
                        "mcap_yi": 0,
                        "pe": 0,
                        "pe_lyr": 0,  # V17.0.23: F10 fallback 无静态PE, 置0(下游 N/A)
                        "turnover": 0,
                    }
                )
            if industry_name:
                return {
                    "industry": industry_name,
                    "my_mcap": 0,
                    "my_rank": my_rank,
                    "industry_count": industry_count,
                    "peers": peers,
                }
    except Exception as _e:
        _debug_log(f"datasource tdx industry analysis f10 error: {_e}")

    return {"industry": "", "my_mcap": 0, "my_rank": 0, "industry_count": 0, "peers": []}


async def get_industry_peers_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """异步版 get_industry_peers"""
    import asyncio

    return await asyncio.to_thread(get_industry_peers, code)


@cached(category="industry_peers_v2", ttl_seconds=TTL["industry_peers_v2"], trading_day=True)
def get_stock_sector_rank(
    code: str, info: Optional[Dict[str, Any]] = None, q: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """V7.5: 板块内排名 — V16.2.17 东财申万二级优先（TDX 兜底）。

    返回: {"rank": int, "total": int, "change_pct": float} 或 None。
    """
    # 0. V16.2.17: 东财申万二级成员（datacenter 一次性映射缓存 + 腾讯实时涨跌幅）
    try:
        _l2 = get_em_industry_l2(code)
        if _l2:
            _l2_members = get_em_industry_members_l2(_l2)
            if _l2_members:
                from core.tdx_client import _tencent_batch_fallback

                _tq = _tencent_batch_fallback(_l2_members) or {}
                _rows = []
                for _mc in _l2_members:
                    if len(_mc) != 6 or not _mc.isdigit() or _mc[:2] not in ("00", "30", "60", "68", "92"):
                        continue
                    _q = _tq.get(_mc) or {}
                    _rows.append({"code": _mc, "change_pct": _q.get("change_pct", 0) or 0})
                _by_chg = sorted(_rows, key=lambda x: x["change_pct"], reverse=True)
                _chg = q.get("change_pct", 0) if q else 0
                if not _chg:
                    _chg = next((r["change_pct"] for r in _by_chg if r["code"] == code), 0)
                for i, _r in enumerate(_by_chg, 1):
                    if _r["code"] == code:
                        return {"rank": i, "total": len(_by_chg), "change_pct": _chg}
    except Exception as _e:
        _debug_log(f"datasource get_stock_sector_rank em_l2 ({code}): {_e}")

    from core.tdx_client import tdx_get_belong_boards, tdx_get_board_members, tdx_get_board_by_name

    # 1. TDX board_members（同源分类，精确匹配）
    boards = tdx_get_belong_boards(code)
    industry_boards = boards.get("industry", []) if boards else []

    if industry_boards:
        primary = industry_boards[0]
        members = tdx_get_board_members(primary["code"])
        if members:
            members_by_chg = sorted(members, key=lambda x: x.get("change_pct", 0), reverse=True)
            for i, m in enumerate(members_by_chg, 1):
                if m["code"] == code:
                    _chg = q.get("change_pct", m["change_pct"]) if q else m["change_pct"]
                    return {"rank": i, "total": len(members), "change_pct": _chg}

    # 2. Fallback: TDX board_list → match by name → board_members
    ind_name = (industry_boards[0].get("name", "") if industry_boards else "") or (
        info.get("industry", "") if info else ""
    )
    if ind_name:
        st = tdx_get_board_by_name(ind_name, board_type=0)
        if st:
            st_sorted = sorted(st, key=lambda x: x.get("change_pct", 0), reverse=True)
            for i, s in enumerate(st_sorted, 1):
                if s["code"] == code:
                    _chg = q.get("change_pct", s["change_pct"]) if q else s["change_pct"]
                    return {"rank": i, "total": len(st), "change_pct": _chg}

    return None


async def get_stock_sector_rank_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_stock_sector_rank"""
    import asyncio

    return await asyncio.to_thread(get_stock_sector_rank, code)


def get_industry_rank_from_zhb(top_n: int = 20) -> List[Dict[str, Any]]:
    """ZHB 本地行业排名（V16.3 O25——用户：行业可比/排名 ZHB 就能获取，参照系 T-1 可接受）。

    从 get_zhb_full_market_snapshot + 申万二级映射（_em_ind_map 缓存）自聚合：
    市值加权涨跌幅 + 涨跌家数 + 领涨股——零网络（ZHB 内存 + L2 JSON 缓存）。
    输出兼容 tdx_get_board_list 格式：[{rank, code, name, change_pct, up_count, down_count,
    leader_name, leader_change, amount_yi, _member_count}]——lng/med/sht 行业排名参照系直用。
    """
    from ._zhb import get_zhb_full_market_snapshot
    try:
        from core.zhb_client import get_zhb

        snap = get_zhb_full_market_snapshot()
        if not snap:
            return []
        zhb = get_zhb()
        industry_map = zhb.industry_map or {}
        # 申万二级映射（东财 L2 缓存——7 天 JSON，不联网）
        _em_ind_map: Dict[str, str] = {}
        try:
            _em_ind_map, _ = get_em_industry_l2_data()
        except Exception:
            pass
        buckets: Dict[str, dict] = {}
        for code, stat in snap.items():
            ind_code = stat.get("industry_code", "")
            # 内联行业段判定（mak _is_industry_code 逻辑：8803/8804/881 通达信行业/申万段）
            _valid_ind = (
                bool(ind_code)
                and len(str(ind_code)) == 6
                and str(ind_code).isdigit()
                and str(ind_code).startswith(("8803", "8804", "881"))
            )
            ind_code = _em_ind_map.get(code, "") or (ind_code if _valid_ind else "")
            if not ind_code:
                continue
            chg = _safe_float(stat.get("change_pct", 0))
            mcap = _safe_float(stat.get("mcap_yi", 0))
            amt = (_safe_float(stat.get("amount", 0)) or 0) / 10000.0
            b = buckets.setdefault(
                ind_code,
                {"_chgs": [], "_mcaps": [], "_amts": [], "_up": 0, "_down": 0,
                 "_best_chg": -999.0, "_best_name": ""},
            )
            b["_chgs"].append(chg)
            b["_mcaps"].append(mcap)
            b["_amts"].append(amt)
            if chg > 0:
                b["_up"] += 1
            elif chg < 0:
                b["_down"] += 1
            if chg > b["_best_chg"]:
                b["_best_chg"] = chg
                b["_best_name"] = zhb.get_stock_name(code) or ""
        rows = []
        for ind_code, b in buckets.items():
            total_mcap = sum(b["_mcaps"])
            if total_mcap > 0 and b["_mcaps"]:
                wchg = sum(c * m for c, m in zip(b["_chgs"], b["_mcaps"])) / total_mcap
            elif b["_chgs"]:
                wchg = sum(b["_chgs"]) / len(b["_chgs"])
            else:
                wchg = 0
            rows.append(
                {
                    "rank": 0,
                    "code": ind_code,
                    "name": industry_map.get(ind_code, ind_code),
                    "change_pct": round(wchg, 2),
                    "up_count": b["_up"],
                    "down_count": b["_down"],
                    "amount_yi": round(sum(b["_amts"]), 2),
                    "leader_name": b["_best_name"],
                    "leader_change": round(b["_best_chg"], 2),
                    "_member_count": len(b["_chgs"]),
                }
            )
        rows.sort(key=lambda x: -x["change_pct"])
        for i, r in enumerate(rows):
            r["rank"] = i + 1
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_industry_rank_from_zhb: {_e}")
        return []


@cached(category="industry_compare", ttl_seconds=TTL["industry_compare"], trading_day=True, valid_if=make_valid_if())
def get_industry_ranking(top_n: int = 20, _tag: str = "report") -> List[Dict[str, Any]]:
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


def get_industry_comparison(top_n: int = 20) -> Dict[str, Any]:
    """V4.2: 全行业排名 → ZHB 本地优先（V16.3 O25——用户：ZHB 就能获取，参照系 T-1 可接受），
    TDX board_list / 东财 push2 兜底。

    Args:
        top_n: 返回行业数量上限（当前未使用，保留参数兼容性）。

    Returns:
        dict: {"top": 涨幅TOP, "bottom": 跌幅TOP, "all": 全部行业, "total": 行业总数}。
    """
    # V16.3 O25: ZHB 本地聚合优先（零网络）——参照系 T-1 可接受
    _zhb_rows = get_industry_rank_from_zhb(top_n)
    if _zhb_rows:
        _top = _zhb_rows[:5]
        _bottom = _zhb_rows[-5:][::-1]
        return {"top": _top, "bottom": _bottom, "all": _zhb_rows, "total": len(_zhb_rows)}
    from core.tdx_client import tdx_get_board_list

    sectors = tdx_get_board_list(0)  # BoardType.HY = 0 行业一级

    if sectors:
        # TDX数据可能缺少实时涨跌幅，尝试用东财push2补充
        em_sectors = _get_eastmoney_industry_sectors()
        if em_sectors:
            # 合并TDX和东财数据
            sector_map = {s.get("code", ""): s for s in sectors}
            for em in em_sectors:
                em_code = em.get("code", "")
                if em_code in sector_map:
                    sector_map[em_code]["change_pct"] = em.get("change_pct", 0)
                    sector_map[em_code]["up_count"] = em.get("up_count", 0)
                    sector_map[em_code]["down_count"] = em.get("down_count", 0)
                    sector_map[em_code]["leader"] = em.get("leader", "")
                    sector_map[em_code]["leader_change"] = em.get("leader_change", 0)
            sectors = list(sector_map.values())

    # 按涨跌幅排序
    sectors.sort(key=lambda x: x.get("change_pct", 0), reverse=True)

    return {
        "top": sectors[:top_n],
        "bottom": sectors[-top_n:],
        "all": sectors,
        "total": len(sectors),
    }


@requires_push2
def _get_eastmoney_industry_sectors() -> List[Dict[str, Any]]:
    """获取东财行业板块实时涨跌幅数据（SKILL.md V3.2 推荐）。

    使用东财push2接口获取行业板块的实时涨跌幅、上涨下跌家数、领涨股等信息。

    Returns:
        list: 行业板块列表，包含涨跌幅、上涨家数、下跌家数、领涨股等字段
    """
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": "m:90+t:2",  # 行业板块
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
        "fid": "f3",  # 按涨跌幅排序
    }
    headers = {"User-Agent": UA}

    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []

        d = r.json()
        # V17.0.26(2026-09-03) DEBT-010: 键名修正 dif → diff（东财 clist 接口返回 data.diff）。
        #   原拼写错误致 items 恒为 [] → 本函数恒返回 [] → 调用方 L2898 `if em_sectors:` 永假，
        #   东财实时涨跌幅补充分支**从未执行**（TDX 板块列表缺实时涨幅时无法补）。
        #   隐蔽性强: 主路径 ZHB 可用时提前返回(L2890)，掩盖了该分支失效。
        #   纯收益修复: HTTP 请求已发出、push2 风控成本已付，此前结果被白白丢弃。
        items = d.get("data", {}).get("diff", [])
        if not items:
            return []

        sectors = []
        for item in items:
            sectors.append(
                {
                    "name": item.get("f14", ""),
                    "code": item.get("f12", ""),
                    "change_pct": item.get("f3", 0),
                    "up_count": item.get("f104", 0),
                    "down_count": item.get("f105", 0),
                    "leader": item.get("f140", ""),
                    "leader_change": item.get("f136", 0),
                }
            )

        return sectors
    except Exception as _e:
        _debug_log(f"datasource _get_eastmoney_industry_sectors: {_e}")
        return []


async def get_industry_comparison_async(session: Any, top_n: int = 20) -> Dict[str, Any]:
    """异步版 get_industry_comparison"""
    import asyncio

    return await asyncio.to_thread(get_industry_comparison, top_n)


def _tdxhy_industry_map() -> Dict[str, str]:
    """V17.0.1g(2026-08-16): TDX 本机行业映射 code→一级行业名(零网络, 进程缓存).

    数据源(field_dict 表头·行业/细分行业唯一来源):
      - tdxhy.cfg(文本 Pipe): 市场|代码|T一级|空|空|X细分 —— 5,641 只 A 股全量
      - hy_tree.xml(GBK): X 码三级树 → 一级名(2 位 X 码)
    用途: 同花顺涨停池(无 sector 字段)的涨停板块分布注入。
    M4(审查 2026-08-16): 异常时保持 None 不固化——允许下次调用重试(文件修复/路径恢复后生效)。
    """
    from ._misc import _tdx_root
    global _TDXHY_CACHE
    if _TDXHY_CACHE is not None:
        return _TDXHY_CACHE
    _m: Dict[str, str] = {}
    try:
        import re as _re
        # 1) hy_tree.xml: X码 → 一级名(层级栈: 2位=一级, 其下节点继承)
        _lvl1 = ""
        _text = open(os.path.join(_tdx_root(), "T0002", "cloud_cfg", "hy_tree.xml"), encoding="gbk", errors="ignore").read()
        for _mn in _re.finditer(r'<node\s[^>]*caption="([^"]*)"[^>]*blockid="X(\d+)"|<node\s[^>]*blockid="X(\d+)"[^>]*caption="([^"]*)"', _text):
            _cap = _mn.group(1) or _mn.group(4)
            _xc = _mn.group(2) or _mn.group(3)
            if len(_xc) == 2:
                _lvl1 = _cap
            else:
                _m["X" + _xc] = _lvl1
        # 2) tdxhy.cfg: code → X细分码(已带 X 前缀) → 一级名
        for _ln in open(os.path.join(_tdx_root(), "T0002", "hq_cache", "tdxhy.cfg"), encoding="gbk", errors="ignore"):
            _p = _ln.rstrip("\n").split("|")
            if len(_p) >= 6 and len(_p[1]) == 6 and _p[1].isdigit():
                _x = _p[5].strip()
                if _x:
                    _m[_p[1]] = _m.get(_x, "") or ""
    except Exception as _e:
        _debug_log(f"_tdxhy_industry_map: {_e}")
        return _m  # 异常不固化, 下次重试
    _TDXHY_CACHE = _m
    return _m


def get_em_industry_l2_data(force_refresh: bool = False) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """V16.2.17: 东财申万二级行业数据（全市场，一次性拉取缓存）。

    返回: (map_l2: {股票代码: 申万二级名}, members_l2: {申万二级名: [成分代码]})
    二级识别: type=2 行业板块中排除一级名单(_EM_INDUSTRY_L1_NAMES)后取 code 最小
    （实测 000100: 电子[1201一级]/光学光电子[1038]/面板[1335] → 光学光电子；
      600519: 食品饮料[438一级]/白酒Ⅱ[1277]/白酒Ⅲ[1575] → 白酒Ⅱ）。
    """
    from ._eastmoney import _em_l2_load_cached
    import json as _json
    import os as _os
    import time as _time

    global _EM_L2_MAP, _EM_L2_MEMBERS, _EM_L2_LOADED_TS
    _now = _time.time()
    if not force_refresh and _EM_L2_MAP is not None and _now - _EM_L2_LOADED_TS < _EM_L2_TTL:
        return _EM_L2_MAP, (_EM_L2_MEMBERS or {})

    _cached = _em_l2_load_cached(_json, _os, _now)
    if not force_refresh and _cached is not None:
        _EM_L2_MAP = _cached
        _EM_L2_LOADED_TS = _now
        return _EM_L2_MAP, (_EM_L2_MEMBERS or {})

    _per_stock: Dict[str, List[Any]] = {}
    _url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    # V16.4.1: try 外初始化——异常路径 L4152 引用会 UnboundLocalError(被调用方吞掉掩盖真错)
    _map_l2: Dict[str, str] = {}
    _members_l2: Dict[str, List[str]] = {}
    try:
        _page = 1
        while True:
            _params = {
                "reportName": "RPT_EM_BOARD_CONSTITUENT", "columns": "ALL",
                "pageNumber": str(_page), "pageSize": "5000",
            }
            _r = em_get(_url, params=_params, headers={"User-Agent": UA}, timeout=30)
            if _r is None:
                break
            _d = _r.json()
            _res = _d.get("result") or {}
            _rows = _res.get("data") or []
            if not _rows:
                break
            for _row in _rows:
                if str(_row.get("BOARD_TYPE_NEW", "")) == "2":
                    _sc = str(_row.get("SECURITY_CODE", ""))
                    _bc = _row.get("BOARD_CODE")
                    _nm = str(_row.get("BOARD_NAME", "")).strip()
                    if _sc and _nm and _nm != "-":
                        try:
                            _per_stock.setdefault(_sc, []).append((int(_bc), _nm))
                        except (TypeError, ValueError):
                            _per_stock.setdefault(_sc, []).append((0, _nm))
            _pages = _res.get("pages") or 1
            if _page >= int(_pages):
                break
            _page += 1
        # 二级识别：排除一级名单后 code 最小；成员表反转
        for _sc, _boards in _per_stock.items():
            _sb = sorted(_boards)
            _l2 = next((nm for _c, nm in _sb if nm not in _EM_INDUSTRY_L1_NAMES), None)
            if not _l2:
                _l2 = _sb[0][1] if _sb else ""
            if _l2:
                _map_l2[_sc] = _l2
                _members_l2.setdefault(_l2, []).append(_sc)
        # 写磁盘缓存（版本隔离 _l2 后缀）
        try:
            _cache_dir = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "cache")
            _os.makedirs(_cache_dir, exist_ok=True)
            for _fn, _obj in (("em_industry_map_l2.json", _map_l2), ("em_industry_members_l2.json", _members_l2)):
                _tmp = _os.path.join(_cache_dir, _fn + ".tmp")
                with open(_tmp, "w", encoding="utf-8") as _f:
                    _json.dump(_obj, _f, ensure_ascii=False)
                _os.replace(_tmp, _os.path.join(_cache_dir, _fn))
        except Exception as _e:
            _debug_log(f"datasource em_l2 cache write: {_e}")
    except Exception as _e:
        _debug_log(f"datasource em_l2 fetch: {_e}")

    _EM_L2_MAP = _map_l2
    _EM_L2_MEMBERS = _members_l2
    _EM_L2_LOADED_TS = _now
    return _EM_L2_MAP, _EM_L2_MEMBERS


def get_em_industry_l2(code: str) -> str:
    """V16.2.17: 单只股票东财申万二级行业（映射缓存命中，零额外请求）。"""
    try:
        _m, _ = get_em_industry_l2_data()
        return _m.get(code, "")
    except Exception as _e:
        _debug_log(f"datasource get_em_industry_l2 ({code}): {_e}")
        return ""


def get_em_industry_members_l2(l2_name: str) -> List[str]:
    """V16.2.17: 东财申万二级板块成分（成员缓存命中，零额外请求）。"""
    try:
        _m, _mb = get_em_industry_l2_data()
        return _mb.get(l2_name, []) if _mb else []
    except Exception as _e:
        _debug_log(f"datasource get_em_industry_members_l2 ({l2_name}): {_e}")
        return []


@requires_push2
def get_em_board_list(board_type: int = 0) -> List[Dict[str, Any]]:
    """V12.0: 获取板块列表（替代 TDX MacClient.get_board_list）。

    使用东财 push2 clist 接口，支持行业/概念/地域板块。

    Args:
        board_type: 0=行业一级, 1=行业二级, 3=地域, 4=概念 (兼容 easy_tdx BoardType)

    Returns:
        list: [{"rank": int, "code": str, "name": str, "price": float,
                "change_pct": float, "leader_name": str, "leader_change": float,
                "up_count": int, "down_count": int}, ...]
    """
    fs = _EM_BOARD_TYPE_FS_MAP.get(board_type)
    if not fs:
        _debug_log(f"datasource get_em_board_list: unsupported board_type={board_type}")
        return []

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "200",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": fs,
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f184",
        "fid": "f3",  # 按涨跌幅排序
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    try:
        r = em_get(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        d = r.json()
        items = d.get("data", {}).get("diff", []) or []
        if isinstance(items, dict):
            items = list(items.values())
        sectors = []
        for i, item in enumerate(items):
            sectors.append(
                {
                    "rank": i + 1,
                    "code": str(item.get("f12", "")),
                    "name": str(item.get("f14", "")),
                    "price": _safe_float(item.get("f2", 0)),
                    "change_pct": _safe_float(item.get("f3", 0)),
                    "leader_name": str(item.get("f140", "")),
                    "leader_change": _safe_float(item.get("f136", 0)),
                    "up_count": int(item.get("f104", 0) or 0),
                    "down_count": int(item.get("f105", 0) or 0),
                }
            )
        return sectors
    except Exception as _e:
        _debug_log(f"datasource get_em_board_list type={board_type}: {_e}")
        return []


@cached(category="board_members", ttl_seconds=TTL["board_members"], trading_day=True,
        valid_if=make_valid_if(min_size=1))
@requires_push2
def get_em_board_members(board_code: str) -> List[Dict[str, Any]]:
    """V12.0: 获取板块成员列表（替代 TDX MacClient.get_board_members）。

    使用东财 push2 clist 接口，fs 参数为 b:BK{code}。

    V17.0.26(2026-09-03) DEBT-012: 补 @cached（公理 A4——网络接口须自带缓存）。
      背景: 本函数走 **push2 主域**（45000/h 封禁 20h，全仓风控最严），此前无缓存；
      DEBT-009 修复后 val 报告开始调用它，调用频次从 0 上升；且 MAC TCP 主路径不可用时
      （盘后/连接失败）med 的 sector_rank、sc 的 industry_peers/industry_compare 会对
      **同一板块重复请求** —— 一次报告内可达数十次。
      TTL 15min 的依据（不是拍脑袋）: 全部 5 处消费方（mak get_sector_stocks /
      med sector_rank / sc industry_peers / sc industry_compare / val 日历效应）
      使用本函数的方式**都是「行业内相对排序参照系」**——按 change_pct 或 mcap_yi 排序后
      取本股名次，或按市值挑可比公司。相对排序对 15min 级价格陈旧不敏感。
      `trading_day=True` 保证跨交易日必失效（成分股名单调整不会被掩盖）。
      `valid_if=make_valid_if(min_size=1)`：空列表**不写缓存**（A4 只缓存非空 + 不掩盖降级信号，
      与 DEBT-006 同理）——否则一次网络抖动产生的 [] 会被缓存 15 分钟。

    Args:
        board_code: 板块代码（如 "BK0447"）

    Returns:
        list: [{"code": str, "name": str, "price": float, "change_pct": float,
                "mcap_yi": float, "turnover": float, "pe": float, "pb": float,
                "main_net_amount": float}, ...]
    """
    # 规范化板块代码：纯数字 → 补 BK 前缀
    if not board_code:
        return []
    bc = board_code.strip()
    if bc.isdigit():
        bc = "BK" + bc
    elif not bc.upper().startswith("BK"):
        bc = "BK" + bc

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "300",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": f"b:{bc}",
        # V17.0.15: 原只取 f23 且注释写 "PE（动）" —— **错的**。跨接口对撞实证
        #   (2026-08-31, 12 采集日 150~238 样本, 2% 容差全 100% 命中):
        #     ulist f9   == push2 f162 = 市盈率(动态)
        #     ulist f114 == push2 f163 = 市盈率（静态）
        #     ulist f115 == push2 f164 = 市盈率（TTM）
        #     ulist f23  == push2 f167 = **市净率 PB**
        #   量级佐证: f9 中位 20.84 / f23 中位 2.22，相差 9.4×——分属 PE 族与 PB 族。
        #   后果: "pe" 实际拿到 PB → med 的 industry_pe 变成**行业平均 PB**，
        #   而 sc_scoring.py:237 拿 pe_ttm(≈20) 与它比较 → `pe_ttm < industry_pe`
        #   几乎恒 False → 「PE低于行业均值」+15 分**永不触发**（静默失效，不报错）。
        #   注: TDX MAC 主路径用的是 pe_dynamic(真 PE)，故本 fix 只在东财兜底路径生效，
        #   并使两条路径口径一致。
        "fields": "f12,f14,f2,f3,f9,f20,f21,f23,f62,f184",
        "fid": "f3",  # 按涨跌幅排序
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    try:
        r = em_get(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        d = r.json()
        items = d.get("data", {}).get("diff", []) or []
        if isinstance(items, dict):
            items = list(items.values())
        members = []
        for item in items:
            members.append(
                {
                    "code": str(item.get("f12", "")),
                    "name": str(item.get("f14", "")),
                    "price": _safe_float(item.get("f2", 0)),
                    "change_pct": _safe_float(item.get("f3", 0)),
                    # f20=总市值(元)，转换为亿元
                    "mcap_yi": _safe_float(item.get("f20", 0)) / 1e8,
                    "turnover": _safe_float(item.get("f184", 0)),  # 换手率
                    # V17.0.15: f9 = 市盈率(动态)，与 TDX 主路径 pe_dynamic 口径一致
                    "pe": _safe_float(item.get("f9", 0)),
                    # V17.0.15: f23 = 市净率 PB（原被误当 PE 使用，见上方 fields 注释）
                    "pb": _safe_float(item.get("f23", 0)),
                    "main_net_amount": _safe_float(item.get("f62", 0)),  # 主力净流入额
                }
            )
        return members
    except Exception as _e:
        _debug_log(f"datasource get_em_board_members {board_code}: {_e}")
        return []


@cached(
    category="industry_classification",
    valid_if=lambda r: isinstance(r, dict) and bool(r.get("industry") or r.get("area")),
)
@requires_push2
def get_em_belong_boards(code: str) -> Dict[str, List[Any]]:
    """V12.0: 获取股票所属板块（替代 TDX MacClient.get_belong_board）。

    使用东财 push2 stock/get 获取个股所属行业，再从板块列表匹配板块代码。
    注：东财 HTTP 接口仅返回行业，概念/地域返回空列表（如有需要可后续扩展）。

    V15.2 P0 修复：原注释错误地认为 f127=板块代码、f128=板块名称，实际：
      - f127 = 行业名称（如"光学光电子"）
      - f128 = 地域板块名称（如"广东板块"）
      - f135 = 数值（某种总市值/成交额，不是板块代码）
      - f136 = 数值（不是板块代码）
    修复后：industry 只用 f127（名称），area 只用 f128（名称），code 字段暂时用名称做 hash。

    Args:
        code: 股票代码（6位数字）

    Returns:
        dict: {"industry": [{"code": str, "name": str}, ...],
               "concept": [], "area": [], "style": []}
    """
    result: Dict[str, List[Any]] = {"industry": [], "concept": [], "area": [], "style": []}
    if not code or len(code) != 6:
        return result

    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    # V15.2 P0 修复: 字段含义纠正
    # f127 = 行业名称（字符串，如"光学光电子"）
    # f128 = 地域板块名称（字符串，如"广东板块"）
    # f135/f136 = 数值（不是板块代码/名称）
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": secid,
        "fields": "f127,f128",
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    try:
        r = em_get(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is not None:
            d = r.json()
            data = d.get("data", {}) or {}
            ind_name = str(data.get("f127", "") or "").strip()
            if ind_name:
                # 名称作为 code（避免空 code），规范化供下游使用
                result["industry"].append({"code": ind_name, "name": ind_name})
            area_name = str(data.get("f128", "") or "").strip()
            if area_name:
                result["area"].append({"code": area_name, "name": area_name})
    except Exception as _e:
        _debug_log(f"datasource get_em_belong_boards stock/get ({code}): {_e}")

    return result


__all__ = [
    'TTL',
    'UA',
    '_EM_BOARD_TYPE_FS_MAP',
    '_EM_INDUSTRY_L1_NAMES',
    '_EM_L2_LOADED_TS',
    '_EM_L2_MAP',
    '_EM_L2_MEMBERS',
    '_EM_L2_TTL',
    '_TDXHY_CACHE',
    '_debug_log',
    '_f',
    '_get_eastmoney_industry_sectors',
    '_load_strategy_config',
    '_safe_float',
    '_tdxhy_industry_map',
    'asyncio',
    'cached',
    'code',
    'em_get',
    'em_secid_prefix',
    'get_em_belong_boards',
    'get_em_board_list',
    'get_em_board_members',
    'get_em_industry_l2',
    'get_em_industry_l2_data',
    'get_em_industry_members_l2',
    'get_industry_comparison',
    'get_industry_comparison_async',
    'get_industry_peers',
    'get_industry_peers_async',
    'get_industry_rank_from_zhb',
    'get_industry_ranking',
    'get_industry_reports',
    'get_stock_sector_rank',
    'get_stock_sector_rank_async',
    'make_valid_if',
    'os',
    'requires_push2',
    'stat',
]
