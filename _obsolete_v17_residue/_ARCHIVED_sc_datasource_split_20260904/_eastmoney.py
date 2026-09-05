"""stock_common/sc_datasource/_eastmoney.py — V17.1 拆包子模块（Facade 重导出，零行为变化）"""
from ._shared import *  # 取得 import 块名 + 常量（含私有，见 _shared.__all__）

def eastmoney_datacenter(
    code: str,
    report_name: str,
    columns: str = "ALL",
    filter_str: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
    page_index: int = 1,
) -> List[Dict[str, Any]]:
    """东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V7.5 新增：HTTP状态码非200时记录日志，业务错误码(status=-1)时记录日志，JSON解析失败时记录日志。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        r = _quick_request(
            DATACENTER_URL,
            params={
                "reportName": report_name,
                "columns": columns,
                "filter": full_filter,
                "pageNumber": str(page_index),
                "pageSize": str(page_size),
                "sortColumns": sort_columns,
                "sortTypes": sort_types,
                "source": "WEB",
                "client": "WEB",
            },
            headers={"User-Agent": UA},
            timeout=15,
        )
        if r is None:
            return []
        # HTTP状态码检查
        if r.status_code != 200:
            _http_logger.error(f"{r.status_code} | {DATACENTER_URL} | {report_name} | {code}")
            return []
        try:
            d = r.json()
        except Exception as _json_err:
            _http_logger.error(
                f"JSONDecodeError | {DATACENTER_URL} | {report_name} | {code} | {_json_err}"
            )
            return []
        # 业务错误码检查
        if isinstance(d, dict) and d.get("status") == -1:
            _biz_logger.error(f"status=-1 | {report_name} | {code} | {d.get('message', '')}")
            return []
        if d.get("result") and d["result"].get("data"):
            return d["result"]["data"]
        return []
    except Exception as _e:
        _debug_log(f"eastmoney_datacenter({code}, {report_name}): {_e}")
        return []

def _em_filter(
    code: str,
    report_name: str,
    extra_filter: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。"""
    return eastmoney_datacenter(
        code,
        report_name,
        filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
        page_size=page_size,
        sort_columns=sort_columns,
        sort_types=sort_types,
    )

async def eastmoney_datacenter_async(
    session: Any,
    code: str,
    report_name: str,
    columns: str = "ALL",
    filter_str: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """async 版：东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        d = await _async_request_with_retry(
            session,
            DATACENTER_URL,
            params={
                "reportName": report_name,
                "columns": columns,
                "filter": full_filter,
                "pageNumber": "1",
                "pageSize": str(page_size),
                "sortColumns": sort_columns,
                "sortTypes": sort_types,
                "source": "WEB",
                "client": "WEB",
            },
            headers={"User-Agent": UA},
            timeout=15,
        )
        if d is None:
            return []
        if isinstance(d, dict) and d.get("status") == -1:
            _biz_logger.error(f"status=-1 | {report_name} | {code} | {d.get('message', '')}")
            return []
        if d.get("result") and d["result"].get("data"):
            return d["result"]["data"]
        return []
    except Exception as _e:
        _debug_log(f"eastmoney_datacenter_async({code}, {report_name}): {_e}")
        return []

async def _em_filter_async(
    session: Any,
    code: str,
    report_name: str,
    extra_filter: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """async 版：东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    return await eastmoney_datacenter_async(
        session,
        code,
        report_name,
        filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
        page_size=page_size,
        sort_columns=sort_columns,
        sort_types=sort_types,
    )

def get_em_batch_quotes(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """V12.0: 东财批量行情查询（替代TDX批量查询，修复URL超长Bug）。

    V17.0(2026-08-15): 改 push2delay 镜像域 + secids 参数(原 fs 返回 data:null);
    V17.0.1a(2026-08-16): 当日进程缓存——增量拉取缺失代码, 命中直接返回。
    """
    if not codes:
        return {}
    # V17.0.1a: 当日缓存命中直接返回(增量)
    global _EM_BATCH_CACHE, _EM_BATCH_CACHE_DATE
    from datetime import datetime as _dt2
    _today2 = _dt2.now().strftime("%Y%m%d")
    if _EM_BATCH_CACHE_DATE != _today2:
        _EM_BATCH_CACHE.clear()
        _EM_BATCH_CACHE_DATE = _today2
    _missing = [c for c in codes if c not in _EM_BATCH_CACHE]
    if not _missing:
        return {c: _EM_BATCH_CACHE[c] for c in codes if c in _EM_BATCH_CACHE}

    # 东财市场代码前缀: 沪市为 1., 深市为 0.
    sh_codes = [f"{em_secid_prefix(c)}{c}" for c in codes if em_secid_prefix(c) == "1."]
    sz_codes = [f"{em_secid_prefix(c)}{c}" for c in codes if em_secid_prefix(c) == "0."]  # V17.0 S3: 统一前缀
    all_formatted_codes = sh_codes + sz_codes

    result = {}

    @requires_push2
    def _fetch_batch(code_chunk):
        if not code_chunk:
            return
        fs_str = ",".join(code_chunk)
        # V17.0(2026-08-15 运行前核查): push2 主域连接级封禁期整体失败+0.4rps 限流
        # (17 chunk × 2.5s = 42.5s)——改 push2delay 镜像域(1.0rps 独立风控, 与采集 ulist239/人气榜先例一致);
        # 盘后/盘中延时 15 分钟对 mak 全景报告可接受
        url = "https://push2delay.eastmoney.com/api/qt/ulist.np/get"
        # V15.2 P0 修复: 增加 mcap_yi 字段（f20 总市值=f116/1e8, f21=f117 流通市值）
        # 之前只拉 f2/f3，导致 val 报告 18 步策略 mcap_yi=0
        # V16.1: 扩展字段包 — f55 EPS/f92 BPS/f126 股息率/f162-167 PE/PB/f174-175 52周高低/f221 报告期
        # V17.0(2026-08-15): + f62 主力净流入(ulist f62 ↔ push2 f137, 跨接口对撞 96.6%)
        # V17.0.16(2026-08-31): 去掉 f66 —— 旧代码误把 f62 当"特大单净"、f66 当"大单净"再相加，
        #   实证 f62 == f66 + f72 (236/236) 证明 f62 已是主力净(含超大单+大单)，相加属重复计数。
        params = {
            "fltt": "2",
            "invt": "2",
            "secids": fs_str,  # V17.0(2026-08-15 冒烟修复): ulist.np/get 参数为 secids(非 fs)——fs 返回 data:null
            "fields": (
                "f12,f14,f2,f3,f20,f21,"
                "f55,f92,f126,f162,f163,f167,f174,f175,f221,"
                "f62"  # V17.0.16: 只取 f62(主力净)；f66 已不再使用（见上方注释）
            ),
        }
        try:
            r = em_get(url, params=params, headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}, timeout=15)
            if r is None:
                return
            d = r.json()
            items = d.get("data", {}).get("diff", [])
            for item in items:
                code = str(item.get("f12", ""))
                name = str(item.get("f14", ""))
                price = _safe_float(item.get("f2", 0))
                change_pct = _safe_float(item.get("f3", 0))
                # V15.2 P0: mcap_yi (f20) 和 float_mcap_yi (f21)
                # V16.3 O17: ulist f20/f21 实测单位是**元**（茅台 1635794278989）——需 /1e8 转亿
                # （此前直接赋值导致批量路径 mcap 错 1e8 倍——canonical L3 单股路径无此问题）
                mcap_yi = _safe_float(item.get("f20", 0)) / 1e8
                float_mcap_yi = _safe_float(item.get("f21", 0)) / 1e8
                if code:
                    result[code] = {
                        "name": name,
                        "price": price,
                        "change_pct": change_pct,
                        "mcap_yi": mcap_yi,
                        "float_mcap_yi": float_mcap_yi,
                        # V16.1: 扩展字段（val 横截面初筛用）
                        "eps": _safe_float(item.get("f55", 0)),
                        "bps": _safe_float(item.get("f92", 0)),
                        "dividend_yield": _safe_float(item.get("f126", 0)),
                        "pe_dynamic": _safe_float(item.get("f162", 0)),
                        "pe_lyr": _safe_float(item.get("f163", 0)),
                        "pe_ttm": _safe_float(item.get("f164", 0)),
                        "pb": _safe_float(item.get("f167", 0)),
                        "high_52w": _safe_float(item.get("f174", 0)),
                        "low_52w": _safe_float(item.get("f175", 0)),
                        "report_period": str(item.get("f221", "")),
                        # V17.0.16(2026-08-31): 主力净流入(万元) = **f62 本身**，不再 + f66。
                        # 旧版按「主力 = f62 + f66」计算，与 stock/get 侧「f137 + f140」是同一个 bug。
                        # 实证（12 采集日 236 样本）：**f62 == f66 + f72 命中 236/236 = 100%**
                        #   → f62 = 主力净(已含超大单+大单)，f66 = 超大单净，f72 = 大单净。
                        # 再加 f66 即重复计一次超大单，虚高约 40%（与 push2 侧同量级）。
                        # 索引对齐仍然成立：ulist f62/f66/f72 ↔ push2 f137/f140/f143（跨接口对撞 96%+）。
                        "main_net_inflow_wan": _safe_float(item.get("f62", 0)) / 1e4,
                    }
        except RateLimitBlockedError:
            # M9 修复：EM 连续 403(IP 被封) 必须显性抛出，不能再被宽 except 吞成空数据
            # （否则"IP 被封"表现为空结果，且无任何失败信号上浮到 run()/main.py）。
            raise
        except Exception as _e:
            _debug_log(f"datasource get_em_batch_quotes error: {_e}")

    chunk_size = 300
    for i in range(0, len(all_formatted_codes), chunk_size):
        chunk = all_formatted_codes[i : i + chunk_size]
        _fetch_batch(chunk)

    for _c, _v in result.items():
        _EM_BATCH_CACHE[_c] = _v  # V17.0.1a: 写回当日缓存
    return result

def get_eastmoney_stock_news(code: str, page_size: int = 20) -> List[Dict[str, Any]]:
    """获取东财个股新闻。

    V9.6: 东财search-api-web HTTP接口已失效（返回passportWeb而非新闻），
    现仅使用 TDX F10 公司报道数据。F10不可用时返回空列表。

    Args:
        code: 股票代码
        page_size: 返回数量上限

    Returns:
        list: 新闻列表，包含标题、发布时间、来源、摘要等字段
    """
    try:
        from core.tdx_client import tdx_get_company_news_f10

        f10_news = tdx_get_company_news_f10(code, count=page_size)
        if f10_news:
            return [
                {
                    "title": n.get('title', ''),
                    "publish_time": n.get('date', ''),
                    "source": "F10",
                    "summary": n.get('summary', ''),
                    "url": n.get('url', ''),
                }
                for n in f10_news
            ]
    except Exception as _e:
        _debug_log(f"datasource tdx company news f10 error: {_e}")
    return []

def get_eastmoney_global_news(page_size: int = 50) -> List[Dict[str, Any]]:
    """获取东财全球资讯（7×24 滚动快讯）。

    使用东财np-weblist接口获取7×24财经快讯，与财联社快讯互为独立备份。

    Args:
        page_size: 返回数量上限

    Returns:
        list: 资讯列表，包含标题、发布时间、内容等字段
    """
    url = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"

    import uuid

    params = {
        "client": "web",
        "biz": "web_724",
        "fastColumn": "102",
        "sortEnd": "",
        "pageSize": str(page_size),
        "req_trace": str(uuid.uuid4()),
    }

    headers = {"User-Agent": UA, "Referer": "https://kuaixun.eastmoney.com/"}

    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []

        d = r.json()
        items = d.get("data", {}).get("fastNewsList", [])

        news_items = []
        for item in items[:page_size]:
            news_items.append(
                {
                    "title": item.get("title", ""),
                    "publish_time": item.get("showTime", ""),
                    "content": item.get("summary", "")[:200],
                    "type": item.get("type", ""),
                }
            )

        return news_items
    except Exception as _e:
        _debug_log(f"datasource get_eastmoney_global_news: {_e}")
        return []

def get_eastmoney_cash_flow(code: str) -> List[Dict[str, Any]]:
    """获取东财现金流量表（新浪xjllb接口已失效，使用东财数据中心替代）

    V9.6: 新增，使用东财数据中心RPT_CASHFLOW表获取现金流量数据。
    """
    data = eastmoney_datacenter(
        code,
        "RPT_CASHFLOW",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=5,
        sort_columns="REPORT_DATE",
        sort_types="-1",
    )
    if not data:
        return []

    rows = []
    for r in data:
        rows.append(
            {
                "报告日": str(r.get("REPORT_DATE", "") or "")[:10],
                "经营活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_OPERATING", "") or "0"),
                "投资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_INVESTING", "") or "0"),
                "筹资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_FINANCING", "") or "0"),
                "现金及现金等价物净增加额": str(r.get("NET_INCREASE_CASH_EQUIVALENTS", "") or "0"),
            }
        )
    return rows

async def get_eastmoney_cash_flow_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 东财现金流量表

    V9.6: 新增，使用东财数据中心RPT_CASHFLOW表获取现金流量数据。
    """
    data = await eastmoney_datacenter_async(
        session,
        code,
        "RPT_CASHFLOW",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=5,
        sort_columns="REPORT_DATE",
        sort_types="-1",
    )
    if not data:
        return []

    rows = []
    for r in data:
        rows.append(
            {
                "报告日": str(r.get("REPORT_DATE", "") or "")[:10],
                "经营活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_OPERATING", "") or "0"),
                "投资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_INVESTING", "") or "0"),
                "筹资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_FINANCING", "") or "0"),
                "现金及现金等价物净增加额": str(r.get("NET_INCREASE_CASH_EQUIVALENTS", "") or "0"),
            }
        )
    return rows

def get_board_fund_flow(board_type: str = "industry", top_n: int = 20) -> List[Dict[str, Any]]:
    """获取板块资金流向（行业/概念/地域板块的主力净流入排名）。

    V16.0 新增，参考 a-stock-data V3.5 `board_fund_flow`。
    2026-08-03 联网验证：83.push2 备用域名可用。
    注意：push2 有 IP 级风控，遇 RemoteDisconnected 需等待 30-60 分钟。

    ⚠️ 遗留(dead-code, 2026-09-01 战略重估标注): 经全仓 grep 确认本函数**未被 5 大脚本活跃路径调用**
    （mak 板块分析走 KPL RealRankingInfo + ZHB 聚合, 不调板块资金流排名）。保留供未来/外部使用, 勿在
    批量管线中新增调用以免触发东财 push2 连接级风控。

    Args:
        board_type: "industry"(行业 m:90 t:2) / "concept"(概念 m:90 t:3) / "area"(地域 m:90 t:1)
        top_n: 返回前 N 个板块

    Returns:
        [{code, name, change_pct, main_net_wan, super_net_wan, large_net_wan, medium_net_wan, small_net_wan, turnover}]
    """
    fs_map = {
        "industry": "m:90+t:2+f:!50",
        "concept": "m:90+t:3+f:!50",
        "area": "m:90+t:1+f:!50",
    }
    fs = fs_map.get(board_type, fs_map["industry"])
    # V16.3 O16: 翻页支持（参考仓库 v3.5.1）——先取首页拿真实 total，top_n>200 才翻页；
    # total 缺失按"不足一页即末页"收敛；提前返空即跳出防死循环。
    _PAGE = 200  # 东财 clist 单页上限
    params_tpl = {
        "po": "1", "np": "1", "fltt": "2", "invt": "2",
        "fs": fs,
        "fields": "f12,f14,f2,f3,f62,f66,f69,f72,f75,f184",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
    }

    def _fetch_page(pn: int, pz: int) -> dict:
        params = dict(params_tpl, pn=str(pn), pz=str(pz))
        try:
            r = _quick_request(
                "https://push2.eastmoney.com/api/qt/clist/get",
                params=params, headers={"User-Agent": UA}, timeout=10,
            )
            if r is None:
                # fallback: 备用域名（83.push2 实测可用）
                r = _quick_request(
                    "http://83.push2.eastmoney.com/api/qt/clist/get",
                    params=params, headers={"User-Agent": UA}, timeout=10,
                )
            if r is None:
                return {}
            d = r.json()
            return d.get("data") or {}
        except Exception as _e:
            _debug_log(f"datasource board_fund_flow page {pn}: {_e}")
            return {}

    try:
        data0 = _fetch_page(1, min(top_n, _PAGE))
        if not data0:
            return []
        total = data0.get("total")
        if isinstance(total, str):
            try:
                total = int(total)
            except ValueError:
                total = None
        diff0 = data0.get("diff") or []
        if isinstance(diff0, dict):
            diff0 = list(diff0.values())
        all_items = list(diff0)
        # 需要翻页：total 存在且 > 当前已取，且 top_n 超过单页
        need = top_n if total is None else min(top_n, total)
        while len(all_items) < need and len(diff0) > 0:
            pn = len(all_items) // _PAGE + 1
            data_n = _fetch_page(pn, _PAGE)
            diff_n = data_n.get("diff") or []
            if isinstance(diff_n, dict):
                diff_n = list(diff_n.values())
            if not diff_n:
                break  # 提前返空即末页（防死循环）
            all_items.extend(diff_n)
        out = []
        for item in all_items[:top_n]:
            out.append(
                {
                    "code": str(item.get("f12", "")),
                    "name": str(item.get("f14", "")),
                    "change_pct": _safe_float(item.get("f3", 0)),
                    "main_net_wan": _safe_float(item.get("f62", 0)) / 1e4,  # 元→万元
                    "super_net_wan": _safe_float(item.get("f66", 0)) / 1e4,
                    "large_net_wan": _safe_float(item.get("f69", 0)) / 1e4,
                    "medium_net_wan": _safe_float(item.get("f72", 0)) / 1e4,
                    "small_net_wan": _safe_float(item.get("f75", 0)) / 1e4,
                    "turnover": _safe_float(item.get("f184", 0)),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource get_board_fund_flow: {_e}")
        return []

def get_eastmoney_minute_fund_flow(code: str) -> List[Dict[str, Any]]:
    """获取东财个股分钟级资金流数据

    V9.6 新增：使用东财push2接口获取分钟级资金流，用于与TDX资金流加权融合。
    数据格式与同花顺/百度资金流不同，但覆盖更稳定。

    ⚠️ 遗留(dead-code, 2026-09-01 战略重估标注): 经全仓 grep 确认**未被 5 大脚本活跃路径调用**
    （主力净额统一走 push2delay f137 / thsdk 口径, 弃用 easy_tdx 原生资金流——见 §12.15.5）。
    保留供未来/外部使用, 勿在批量管线中新增调用。

    Returns:
        分钟级资金流列表，每项包含时间/主力净流入/小单净流入/中单净流入/大单净流入
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": "0",
        "klt": "1",  # 1分钟
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        # V16.2.4: 多域轮换（分钟级延时域可能无窗口，失败时返回空由调用方降级）
        r = _em_fflow_request("/api/qt/stock/fflow/kline/get", params)
        if r is None:
            return []
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return []

        result = []
        for line in klines:
            parts = line.split(",")
            if len(parts) >= 11:
                result.append(
                    {
                        "time": parts[0],
                        "main_net_inflow": _safe_float(parts[1]),  # 主力净流入
                        "small_net_inflow": _safe_float(parts[2]),  # 小单净流入
                        "medium_net_inflow": _safe_float(parts[3]),  # 中单净流入
                        "large_net_inflow": _safe_float(parts[4]),  # 大单净流入
                        "super_net_inflow": _safe_float(parts[5]),  # 超大单净流入
                    }
                )
        return result
    except Exception as _e:
        _debug_log(f"datasource get_eastmoney_minute_fund_flow ({code}): {_e}")
        return []

def get_fund_flow_weighted(code: str, tdx_data: Any = None) -> Dict[str, Any]:
    """获取加权融合资金流数据（V9.6 新增）

    融合TDX、东财分钟级资金流，按权重加权计算：
    - TDX TCP资金流：权重 1.0（最实时、最准确）
    - 东财分钟级资金流：权重 0.6（覆盖稳定、数据量大）

    ⚠️ 遗留(dead-code, 2026-09-01 战略重估标注): 经全仓 grep 确认**未被 5 大脚本活跃路径调用**
    （主力净额统一走 push2delay f137 / thsdk 口径, 弃用 easy_tdx 原生资金流——见 §12.15.5）。
    保留供未来/外部使用, 勿在批量管线中新增调用。

    Args:
        code: 股票代码
        tdx_data: TDX资金流数据（如已获取，避免重复请求）

    Returns:
        加权融合后的资金流数据
    """
    # M18 清理：本函数为不完整实现（仅记录 source/权重/标记，未算加权融合值），
    # 且全仓无调用方（仅 stock_common.__init__ 转发），属死代码。保留签名以避免
    # 外部意外 import 缺失，但明确标记不再使用；如需加权资金流请直接用
    # get_em_fund_flow / tdx_get_fund_flow。
    _debug_log(f"get_fund_flow_weighted 已废弃(无调用方): {code}")
    return {"primary_source": "none", "sources": {}, "deprecated": True}

def get_history_fund_flow_120d(code: str, days: int = 60, prefer: str = "auto") -> Dict[str, Any]:
    """V16.2.4 (D2): 统一 120 日资金流入口（消除 get_fund_flow_120d 在 sht/med 的双实现）。

    Args:
        code: 股票代码
        days: 天数（默认 60）
        prefer: "tdx"=TDX 优先→东财 fallback（sht 短线口径）；
                "em"=仅东财（med 中线口径）；"auto"=TDX 优先

    Returns:
        {"data": [dict(元)] 或 [], "error": str, "source": str}
        与 med/sht 原有 get_fund_flow_120d 返回结构完全一致。

    ⚠️ V17.0.13 资金流口径（easy_tdx #55，2026-08-30）：本项目主力净额统一走
    东财 push2 f137+f140 / thsdk 口径，**弃用 easy_tdx 原生资金流**（其 get_fund_flow
    基于 0x0fb5 逐笔聚合、按成交额分档，与东财/同花顺主力净流入不可比，重合度 ~14%）。
    下方 `tdx_get_history_fund_flow` 已委托东财 HTTP，最终仍归东财口径，安全；
    但若 future 改回原生 easy_tdx 资金流，须先评估口径差异，禁止直接当主力净额源。
    """
    def _norm_ff(data):
        """V16.3 O19: 强制归一为 dict 列表（单位元）——历史遗留 float 列表（万元）自动转 dict(元)。"""
        if data and isinstance(data[0], (int, float)):
            return [
                {
                    "date": "",
                    "main_net": v * 1e4,
                    "super_net": 0,
                    "large_net": 0,
                    "mid_net": 0,
                    "small_net": 0,
                }
                for v in data
            ]
        return data

    if prefer != "em":
        try:
            from core.tdx_client import tdx_get_history_fund_flow

            _tdx = tdx_get_history_fund_flow(code, days)
            if _tdx:
                return {"data": _norm_ff(_tdx), "error": "", "source": "tdx"}
        except Exception as _e:
            _debug_log(f"datasource get_history_fund_flow_120d tdx ({code}): {_e}")
    try:
        _em = get_em_history_fund_flow(code, days)
        if _em:
            return {"data": _norm_ff(_em), "error": "", "source": "eastmoney"}
    except Exception as _e:
        _debug_log(f"datasource get_history_fund_flow_120d em ({code}): {_e}")
    return {"data": [], "error": "资金流数据获取失败"}

def _em_l2_load_cached(_json, _os, _now) -> Optional[Dict[str, str]]:
    """读磁盘缓存（两级：code→二级名、name→成员）。返回 l2_map 或 None。"""
    _d = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    global _EM_L2_MEMBERS
    _mp = _os.path.join(_d, "cache", "em_industry_map_l2.json")
    _mb = _os.path.join(_d, "cache", "em_industry_members_l2.json")
    if not (_os.path.exists(_mp) and _os.path.exists(_mb)):
        return None
    try:
        if _now - _os.path.getmtime(_mp) > _EM_L2_TTL or _now - _os.path.getmtime(_mb) > _EM_L2_TTL:
            return None
        with open(_mp, encoding="utf-8") as _f:
            _m = _json.load(_f)
        with open(_mb, encoding="utf-8") as _f:
            _mbd = _json.load(_f)
        if isinstance(_m, dict) and isinstance(_mbd, dict):
            _EM_L2_MEMBERS = {k: list(v) for k, v in _mbd.items()}
            return _m
    except Exception as _e:
        _debug_log(f"datasource em_l2 cache read: {_e}")
    return None

def cls_telegraph(page_size: int = 50) -> List[Dict[str, Any]]:
    """财联社电报（全市场实时快讯）。v1 API + 本地签名，零 key。

    V9.6 新增：使用 cls.cn/v1/roll/get_roll_list，签名算法为 md5(sha1(按key字典序拼接的query串))。
    与东财7×24快讯互为独立备份（不同源、不同风控面）。

    Args:
        page_size: 返回条数，默认50条

    Returns:
        快讯列表，包含 title/content/time 字段
    """
    import hashlib
    from datetime import datetime

    params = {
        "appName": "CailianpressWeb",
        "os": "web",
        "sv": "7.7.5",
        "last_time": "",
        "refresh_type": "1",
        "rn": str(page_size),
    }
    qs = "&".join(f"{k}={params[k]}" for k in sorted(params))
    sign = hashlib.md5(hashlib.sha1(qs.encode()).hexdigest().encode()).hexdigest()
    url = f"https://www.cls.cn/v1/roll/get_roll_list?{qs}&sign={sign}"

    try:
        r = _quick_request(
            url, headers={"User-Agent": UA, "Referer": "https://www.cls.cn/"}, timeout=10
        )
        if r is None:
            return []
        d = r.json()
        if d.get("errno") != 0:
            _debug_log(f"cls_telegraph error: errno={d.get('errno')} errmsg={d.get('errmsg')}")
            return []

        rows = []
        for item in d.get("data", {}).get("roll_data", []) or []:
            ts = item.get("ctime")
            t = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            # V16.1: 保留 stock_list/subjects（供 sht 关联股票分析）
            stock_list = item.get("stock_list") or []
            subjects = item.get("subjects") or []
            rows.append(
                {
                    "title": item.get("title", "") or item.get("brie", ""),
                    "content": item.get("content", "") or item.get("brie", ""),
                    "time": t,
                    "level": item.get("level", ""),
                    "reading_num": item.get("reading_num", 0),
                    "stock_list": [
                        {
                            "code": str(s.get("StockID", "") or s.get("stock_code", "")),
                            "name": str(s.get("name", "") or s.get("stock_name", "")),
                            "pct": s.get("RiseRange"),
                        }
                        for s in stock_list
                        if isinstance(s, dict)
                    ],
                    "subjects": [
                        {
                            "id": s.get("subject_id"),
                            "name": s.get("subject_name", ""),
                        }
                        for s in subjects
                        if isinstance(s, dict)
                    ],
                }
            )
        return rows
    except Exception as _e:
        _debug_log(f"datasource cls_telegraph: {_e}")
        return []

def dragon_tiger_backup(trade_date: str) -> Dict[str, Any]:
    """龙虎榜官方备用源（东财被封时用）：上交所+深交所官方，零鉴权权威一手，含营业部席位。

    Args:
        trade_date: 交易日，格式 YYYY-MM-DD

    Returns:
        包含深交所结构化数据和上交所原始文件内容的字典
    """
    import urllib.request
    import ssl

    out = {"date": trade_date, "sse_raw": "", "szse": []}
    _ctx = ssl._create_unverified_context()

    # 深交所龙虎榜
    su = (
        "https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON"
        f"&CATALOGID=1842_xxpl&TABKEY=tab1&txtStart={trade_date}&txtEnd={trade_date}&random=0.9"
    )
    try:
        req = urllib.request.Request(
            su,
            headers={
                "User-Agent": UA,
                "Referer": "https://www.szse.cn/disclosure/supervision/dealinfo/index.html",
            },
        )
        # V16.3 C1: 备胎源裸 urlopen 补节流（_DOMAIN_LIMITS 的 szse 域 3.0rps 不覆盖此直连路径）
        try:
            from stock_common.sc_network import _gen_wait_process_interval
            _gen_wait_process_interval()
        except Exception:
            pass
        # V16.3 O14: 备胎源强制直连（ProxyHandler({}) 忽略系统代理——GD 外全部直连）
        # V16.3 O22: OpenerDirector.open 不接受 context 关键字（原 TypeError 使备胎源永久失效）——
        # 自定义 SSL context 通过 HTTPSHandler 注入
        _opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPSHandler(context=_ctx),
        )
        with _opener.open(req, timeout=15) as r:
            d = json.loads(r.read())
        if isinstance(d, list) and d:
            for row in d[0].get("data", []):
                out["szse"].append(
                    {
                        "code": row.get("zqdm"),
                        "name": row.get("zqjc"),
                        "amount": row.get("cjje"),
                        "reason": row.get("plyy"),
                        "volume": row.get("cjsl"),
                        "note": row.get("bz"),
                    }
                )
    except Exception as _e:
        _debug_log(f"dragon_tiger_backup szse: {_e}")

    # 上交所龙虎榜（JSONP格式）
    eu = (
        "https://query.sse.com.cn/infodisplay/showTradePublicFile.do?"
        f"jsonCallBack=cb&isPagination=false&dateTx={trade_date}"
    )
    try:
        req = urllib.request.Request(
            eu,
            headers={
                "User-Agent": UA,
                "Referer": "https://www.sse.com.cn/disclosure/diclosure/public/",
            },
        )
        # V16.3 C1: 备胎源裸 urlopen 补节流
        try:
            from stock_common.sc_network import _gen_wait_process_interval
            _gen_wait_process_interval()
        except Exception:
            pass
        # V16.3 O14: 强制直连（忽略系统代理）
        _opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with _opener.open(req, timeout=15) as r:
            t = r.read().decode("utf-8", "ignore")
        if "(" in t and ")" in t:
            json_str = t[t.index("(") + 1 : t.rindex(")")]
            d = json.loads(json_str)
            out["sse_raw"] = "\n".join(d.get("fileContents", []))
    except Exception as _e:
        _debug_log(f"dragon_tiger_backup sse: {_e}")

    return out

def fund_flow_backup(code: str, days: int = 60) -> List[Dict[str, Any]]:
    """个股资金流备用源（东财被封时用）：新浪，日度四档单净额。

    Args:
        code: 股票代码
        days: 获取天数，默认60天

    Returns:
        资金流列表，包含日期、主力/大单/中单/小单净流入
    """
    # V16.3 O16: 北交所 920/8/4 号段走 bj 前缀（此 URL 当前未用 prefix，保留统一口径）
    prefix = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("sh" if code.startswith("6") else "sz")
    url = (
        "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_bkzj_bk"
    )
    params = {"page": "1", "num": str(days), "sort": "netamount", "asc": "0", "fenlei": "1"}

    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        d = r.json()
        if isinstance(d, list):
            return d
        return []
    except Exception as _e:
        _debug_log(f"datasource fund_flow_backup ({code}): {_e}")
        return []

def get_dragon_tiger_board(
    code: str, days: int = 30, include_seats: bool = True, enhance_seats: bool = True
) -> Dict[str, Any]:
    """V7.5: 统一龙虎榜查询（单只股票）。

    V8.5新增：enhance_seats参数，启用后自动调用seat_db增强席位分析。
    V10.2修复：移除 today_str 参数（改为内部自动计算），避免跨日缓存 key 污染。

    Args:
        code: 6位股票代码
        days: 回溯天数（sht默认30，med默认180）
        include_seats: 是否查询席位详情（默认True，设为False可减少2次API请求）
        enhance_seats: V8.5新增，是否增强席位分析（默认True，添加席位等级/风格/溢价信号）

    Returns:
        {
          "records": [{date, reason, net_buy, turnover}, ...],
          "seats": {"buy": [{name, buy_amt, sell_amt, net}, ...], "sell": [...]},
          "institution": {"buy_amt", "sell_amt", "net_amt"},
          "net_sum_5d": float,        # V7.5新增：近5日净额累加
          "net_sum_30d": float,       # V7.5新增：近30日（或days）净额累加
          "consecutive_net_buy_days": int,  # V7.5新增：连续净买入天数
          "seat_analysis": {...},     # V8.5新增：enhance_seats=True时返回
        }

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    # V10.2: today_str 内部自动计算，不作为函数参数（避免污染缓存 key）
    today_str = datetime.now().strftime("%Y-%m-%d")
    start_str = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=days)).strftime(
        "%Y-%m-%d"
    )
    records = []
    data = eastmoney_datacenter(
        code,
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{start_str}')(TRADE_DATE<='{today_str}')",
        page_size=50,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )
    for row in data:
        rec = {
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
        }
        # V16.1: 保留高价值字段（sht 用：买卖占比/分析文本/偏离度）
        if row.get("EXPLAIN"):
            rec["explain"] = row["EXPLAIN"]
        if row.get("BUY_RATIO") is not None:
            rec["buy_ratio"] = round(_safe_float(row.get("BUY_RATIO")), 2)
        if row.get("SELL_RATIO") is not None:
            rec["sell_ratio"] = round(_safe_float(row.get("SELL_RATIO")), 2)
        if row.get("DEAL_NET_RATIO") is not None:
            rec["net_ratio"] = round(_safe_float(row.get("DEAL_NET_RATIO")), 2)
        if row.get("ACCUM_AMOUNT") is not None:
            rec["accum_amount"] = _safe_float(row.get("ACCUM_AMOUNT"))
        if row.get("FREE_MARKET_CAP") is not None:
            rec["free_market_cap"] = _safe_float(row.get("FREE_MARKET_CAP"))
        # D1-D5 涨跌偏离度（龙虎榜判定依据）
        for _dn in ("D1", "D2", "D5", "D10", "D20", "D30"):
            _k = f"{_dn}_CLOSE_ADJCHRATE"
            if row.get(_k) is not None:
                rec[f"dev_{_dn.lower()}"] = round(_safe_float(row.get(_k)), 3)
        records.append(rec)

    seats: Dict[str, List[Any]] = {"buy": [], "sell": []}
    institution: Dict[str, float] = {"buy_amt": 0.0, "sell_amt": 0.0, "net_amt": 0.0}

    if records and include_seats:
        latest_date = records[0]["date"]
        # 买入/卖出席席：用最新上榜日期 + SECURITY_CODE 过滤（单引号日期）
        buy_data = eastmoney_datacenter(
            code,
            "RPT_BILLBOARD_DAILYDETAILSBUY",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
            page_size=50,
            sort_columns="BUY",
            sort_types="-1",
        )
        for row in buy_data[:5]:
            seats["buy"].append(
                {
                    "name": row.get("OPERATEDEPT_NAME", ""),
                    "code": str(row.get("OPERATEDEPT_CODE", "")),
                    "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                    "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                    "net": round((row.get("NET") or 0) / 10000, 1),
                }
            )
        sell_data = eastmoney_datacenter(
            code,
            "RPT_BILLBOARD_DAILYDETAILSSELL",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
            page_size=50,
            sort_columns="SELL",
            sort_types="-1",
        )
        for row in sell_data[:5]:
            seats["sell"].append(
                {
                    "name": row.get("OPERATEDEPT_NAME", ""),
                    "code": str(row.get("OPERATEDEPT_CODE", "")),
                    "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                    "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                    "net": round((row.get("NET") or 0) / 10000, 1),
                }
            )
        # 机构专用席位（code == "0" 为机构专用）
        for row in buy_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["buy_amt"] += row.get("BUY") or 0
        for row in sell_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["sell_amt"] += row.get("SELL") or 0
        institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
        institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
        institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)

    # V7.5新增：主力净额连续性统计
    net_sum_5d = round(sum(r["net_buy"] for r in records[:5]), 1)
    net_sum_30d_or_days = round(sum(r["net_buy"] for r in records), 1)
    consecutive_net_buy_days = sum(1 for r in records if r["net_buy"] > 0)

    result = {
        "records": records,
        "seats": seats,
        "institution": institution,
        "net_sum_5d": net_sum_5d,
        "net_sum_30d": net_sum_30d_or_days,
        "consecutive_net_buy_days": consecutive_net_buy_days,
    }

    # V8.5新增：席位增强分析
    if enhance_seats and (seats.get("buy") or seats.get("sell")):
        try:
            from stock_common.seat_db import enhance_lhb_seats

            result["seat_analysis"] = enhance_lhb_seats({"seats": seats})
        except ImportError:
            pass

    return result

def get_recent_dragon_tiger(days: int = 5) -> Dict[str, Any]:
    """V7.5: 全市场龙虎榜上榜记录（用于异动扫描和席位活跃度策略）。

    Returns:
        { stock_code: {name, reason, net_buy, turnover, date}, ... }

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    url = DATACENTER_URL
    try:
        td = datetime.now().strftime("%Y-%m-%d")
        sd = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        params = {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE,EXPLANATION,BILLBOARD_NET_AMT,TURNOVERRATE",
            "filter": f"(TRADE_DATE>='{sd}')(TRADE_DATE<='{td}')",
            "pageNumber": "1",
            "pageSize": "200",
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1",
            "source": "WEB",
            "client": "WEB",
        }
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return {}
        d = r.json()
        data = d.get("result", {}).get("data", []) or []
        result = {}
        for row in data:
            code = str(row.get("SECURITY_CODE", ""))
            if code not in result:
                result[code] = {
                    "name": row.get("SECURITY_NAME_ABBR", ""),
                    "reason": row.get("EXPLANATION", ""),
                    "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
                    "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
                    "date": str(row.get("TRADE_DATE", "") or "")[:10],
                }
        return result
    except Exception as _e:
        _debug_log(f"datasource get_recent_dragon_tiger ({days}d): {_e}")
        return {}

async def get_dragon_tiger_board_async(
    session, code: str, days: int = 30, include_seats: bool = True, enhance_seats: bool = True
) -> Dict[str, Any]:
    """异步版: 单只股票龙虎榜查询（代理到同步版）。

    V10.2: 移除 today_str 参数（同步版已内部自动计算）。
    """
    return await asyncio.to_thread(get_dragon_tiger_board, code, days, include_seats, enhance_seats)

async def get_recent_dragon_tiger_async(session, days: int = 5) -> Dict[str, Any]:
    """异步版: 全市场龙虎榜上榜记录（代理到同步版）。"""
    return await asyncio.to_thread(get_recent_dragon_tiger, days)

def get_em_quote_full(code: str) -> Dict[str, Any]:
    """V15.2 P0 修复: 通过东财 push2 stock/get 获取完整行情。

    V16.3.3: host 参数化重构——本函数走 push2 主域（风控最严，最后手段）；
    常规兜底请用 get_em_quote_full_delay（push2delay 镜像域，风控独立）。
    """
    return _em_quote_full_impl(code, "https://push2.eastmoney.com/api/qt/stock/get")

def get_em_quote_full_delay(code: str) -> Dict[str, Any]:
    """V16.3.3 (2026-08-10 字典 12.15.5): push2delay 镜像域版全字段行情。

    2026-08-10 实测：push2 主域连接级风控（RemoteDisconnected）；push2delay 风控独立、
    114 字段全量可用、延时 15 分钟非盘中无影响——统一层 L3 东财兜底应优先本函数。

    V17.0.26(2026-09-03): 加 @cached——原每次调用直打 push2delay（单股 sht/med/lng 报告
    每只多次、重跑 val 全市场重复打），违反字典 §12.15.5「push2delay 镜像域应优先缓存以降频」。
    trading_day=True 保证日级数据次日 9:30 刷新（15min 延时数据缓存一天无影响）；
    valid_if 拒绝空/全零行情避免投毒。数据_provider 的进程内 _PD_EXTRA_CACHE 仍做单 run 兜底去重。
    """
    return _em_quote_full_impl(code, "https://push2delay.eastmoney.com/api/qt/stock/get")

def get_em_ulist_batch(codes: List[str], fields: str = _ULIST_BATCH_FIELDS) -> List[Dict[str, Any]]:
    """V17.0.26: push2delay ulist.np 批量行情取数，返回**原始 diff 记录列表**。

    背景(DEBT-011)：原先这段取数内联在 `core/data_provider.prefetch_quote_batch` 里
    直连裸 HTTP，违反公理 A1（数据访问收口）。本函数把它下沉到适配器层。

    分层约定（**重要**）:
      - 本函数**只取数、不做业务语义映射**：返回原始 f2/f12/... 记录，
        字段→业务名的映射与单位换算由调用方（Tier1 门面 data_provider）负责。
        这样"取数在适配器、语义在门面"，避免语义散落两处。
      - 安全域：固定 push2delay **镜像域**（风控独立），严禁 push2 主域
        （45000/h 封禁 20h）。
      - 自动分批：>300 只按 300/批拆分。
      - 容错：单批失败（返回 None）或抛异常 → 跳过该批，不冒泡中断调用方。

    关于缓存（公理 A4，有意不加 @cached，详见 DEBT-011 台账论证）:
      - 批量接口若按 codes 组合做 key，组合数爆炸（sht 35 只的任意子集），
        命中率极低，且 300 个 code 拼出的 key ≈ 2.1KB，SQLite 索引效率低；
      - 真正的去重由**调用方门面层按 code 粒度**完成（prefetch_quote_batch 的
        _BATCH_QUOTE_CACHE 只把 missing 的 code 传下来），比按批组合缓存更有效；
      - 跨运行的单股行情缓存已由 `get_em_quote_full_delay` 覆盖。

    Args:
        codes: 股票代码列表（6 位纯数字，如 ["600519", "000001"]）
        fields: 东财字段集；默认覆盖行情/OHLC/市值。
                **不含估值字段** —— 实测 ulist.np 的 f162/f167/f126 恒返回 "-"
                （与 stock/get 单股接口语义不同），估值须走单股接口补齐。

    Returns:
        list: 原始 diff 记录列表（每条 dict，键为 "f2"/"f12" 等东财字段码）。
              全部失败返回 []（**只返回非空结果**，符合公理 A4）。
    """
    if not codes:
        return []

    # 92 北交所须先于 9 判定，统一走 em_secid_prefix（勿手写 startswith("9")）
    from stock_common.sc_utils import em_secid_prefix
    from stock_common import _quick_request

    rows: List[Dict[str, Any]] = []
    for i in range(0, len(codes), _ULIST_BATCH_SIZE):
        chunk = codes[i : i + _ULIST_BATCH_SIZE]
        secids = ",".join(em_secid_prefix(c) + c for c in chunk)
        try:
            r = _quick_request(
                "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
                params={"fltt": "2", "invt": "2", "secids": secids, "fields": fields},
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=10,
            )
            if r is None:      # 风控/封禁跳过，与 `_quick_request` 的 None 约定一致
                continue
            diff = (r.json().get("data") or {}).get("diff") or []
            # 东财偶发以 dict（下标→记录）形式返回，统一摊平为 list
            if isinstance(diff, dict):
                diff = list(diff.values())
            rows.extend(x for x in diff if isinstance(x, dict))
        except Exception as _e:
            _debug_log(f"datasource get_em_ulist_batch chunk[{i}:{i + _ULIST_BATCH_SIZE}]: {_e}")
            continue
    return rows

def _em_quote_full_impl(code: str, host: str = "https://push2delay.eastmoney.com/api/qt/stock/get") -> Dict[str, Any]:
    """内部实现：host 参数化的全字段行情获取（f43-f221，字典 12.9.1）。

    ZHB tdxstat.cfg 35 字段中无 price/change_pct/open/high/low/last_close 等行情字段，
    只能从 HTTP 接口拿。push2 stock/get 是最权威的实时行情源（盘后返回收盘价）。

    Returns:
        dict: {
            "price": float,           # f43  现价（盘后=昨收）
            "open": float,            # f46  今开
            "high": float,            # f44  最高
            "low": float,             # f45  最低
            "last_close": float,      # f60  昨收
            "change_pct": float,      # f170 涨跌幅(%)（push2 直接给出，不需要用 price-昨收 算）
            "amplitude_pct": float,   # f171 振幅(%)
            "change_amt": float,      # f169 涨跌额
            "volume_hand": float,     # f47  成交量(手)
            "amount_wan": float,      # f48  成交额(元→万元)
            "turnover_pct": float,    # f168 换手率(%)
            "pe_ttm": float,          # f164 PE(TTM) (fltt=2 下为浮点，无需 /100) — 🔴2026-09-01 纠正：f164=T重TTM，f163才是静态PE
            "pe_lyr": float,           # f163 静态PE(LYR, 现价÷年报EPS)
            "pe_dynamic": float,
            "pb": float,
            "mcap_yi": float,         # f116 总市值(元→亿元)
            "float_mcap_yi": float,   # f117 流通市值(元→亿元)
            "total_shares": float,    # f84  总股本(股→万股)
            "float_shares": float,    # f85  流通股本(股→万股)
            "name": str,              # f58  股票名称（最新）
            "industry": str,          # f127 行业名称
            "board": str,             # f128 地域板块名称
            "list_date": str,         # f189 上市日期
            "data_date": str,         # 行情快照日期
            # V17.0.7 财务 TTM 族（口径经 fuyao 官方报表终判）:
            "ocf_ttm": float,           # f103 经营活动现金流量净额 TTM (元)
            "revenue_ttm": float,       # f104 营业总收入 TTM (元)
            "net_profit_period": float, # f105 归母净利润 最新报告期 (元)
            "eps_deduct_ttm": float,    # f108 扣非每股收益 TTM (元/股)
            "net_profit_annual": float, # f109 归母净利润 最新年报 (元)
            "eps_annual": float,        # f160 年报EPS (=f109/f84) (元/股)
            "undist_profit_ps": float,  # f190 每股未分配利润 (元/股)
        }
    """
    if not code or len(code) != 6:
        return {}
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    url = host
    # V16.1: 字段包从 19 个扩展为已验证字段包（2026-08-04 官方 TdxQuant 交叉验证）
    #   f51/f52=涨停/跌停价、f55=EPS、f92=BPS、f126=股息率、f162-167=PE×3/PB
    #   f174/f175=52周高低、f137-146=资金流12字段、f198=行业码、f80=交易时段
    #   f129=概念列表（V16.1.7: 概念链 push2 兜底源）
    # 生产字段包（固定，非 f1-f250 全量，防风控）
    params = {
        "fltt": "2",
        "invt": "2",
        "secid": secid,
        "fields": (
            "f43,f44,f45,f46,f47,f48,f57,f58,f60,f84,f85,"
            "f116,f117,f127,f128,f129,f168,f169,f170,f171,f189,"  # V16.2.3: f168 换手率补回（sht 换手率 0.00%）
            "f51,f52,f55,f92,f126,f162,f163,f164,f165,f166,f167,"
            "f174,f175,f198,f80,f221,"  # V16.2: f221 报告期
            # V17.0.16: 补 f149(小单净) —— 旧版只取 f135-f146，缺小单档，
            # 导致四档占比之和不足 100%（大盘股缺 ~3%，小盘股缺 ~38%）。
            "f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f149,"
            "f178,"
            # V17.0.7(2026-08-25 字典终破): 财务 TTM 族——f103 经营现金流净额(TTM 元)/
            # f104 营业总收入(TTM 元)/f105 归母净利(最新报告期 元)/f108 扣非EPS(TTM)/
            # f109 归母净利(最新年报 元)/f160 年报EPS/f190 每股未分配利润
            "f103,f104,f105,f108,f109,f160,f190"
        ),
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        if r is None:
            return {}
        d = r.json()
        if not d or "data" not in d or not d["data"]:
            return {}
        data = d["data"]
        result: Dict[str, Any] = {}

        # 价格类（push2 用 fltt=2/invt=2 时，f43/f44/f45/f46/f60/f169 直接是元为单位的 float）
        for src, dst in [
            ("f43", "price"),
            ("f44", "high"),
            ("f45", "low"),
            ("f46", "open"),
            ("f60", "last_close"),
            ("f169", "change_amt"),
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 涨跌幅/振幅/换手率（push2 直接给出数字，单位 %）
        for src, dst in [
            ("f170", "change_pct"),
            ("f171", "amplitude_pct"),
            ("f168", "turnover_pct"),
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 成交量(手) — push2 f47 单位是手
        vol_hand = data.get("f47")
        if vol_hand is not None and vol_hand != "-":
            try:
                result["volume_hand"] = float(vol_hand)
            except (TypeError, ValueError):
                pass
        # 成交额(元) — push2 f48 单位是元，转万元
        amt_yuan = data.get("f48")
        if amt_yuan is not None and amt_yuan != "-":
            try:
                result["amount_wan"] = float(amt_yuan) / 10000.0
            except (TypeError, ValueError):
                pass

        # 总市值/流通市值（push2 f116/f117 单位是元，转亿元）
        mcap_yuan = data.get("f116")
        if mcap_yuan is not None and mcap_yuan != "-":
            try:
                result["mcap_yi"] = float(mcap_yuan) / 1e8
            except (TypeError, ValueError):
                pass
        float_mcap_yuan = data.get("f117")
        if float_mcap_yuan is not None and float_mcap_yuan != "-":
            try:
                result["float_mcap_yi"] = float(float_mcap_yuan) / 1e8
            except (TypeError, ValueError):
                pass

        # 股本（push2 f84/f85 单位是股，转万股）
        total_shares = data.get("f84")
        if total_shares is not None and total_shares != "-":
            try:
                result["total_shares"] = float(total_shares) / 10000.0
            except (TypeError, ValueError):
                pass
        float_shares = data.get("f85")
        if float_shares is not None and float_shares != "-":
            try:
                result["float_shares"] = float(float_shares) / 10000.0
            except (TypeError, ValueError):
                pass

        # 名称/行业/地域/上市日期
        name = data.get("f58")
        if name and isinstance(name, str):
            result["name"] = name
        industry = data.get("f127")
        if industry and isinstance(industry, str):
            result["industry"] = industry
        board = data.get("f128")
        if board and isinstance(board, str):
            result["board"] = board
        # V16.1.7: f129 概念列表（逗号分隔 → list，概念链 push2 兜底源）
        concepts_raw = data.get("f129")
        if concepts_raw and isinstance(concepts_raw, str):
            result["concepts"] = [c.strip() for c in concepts_raw.split(",") if c.strip()]
        list_date = data.get("f189")
        if list_date:
            try:
                ld = str(int(list_date))
                if len(ld) == 8:
                    result["list_date"] = f"{ld[:4]}-{ld[4:6]}-{ld[6:8]}"
            except (TypeError, ValueError):
                pass

        # ─────────────────────────────────────────────
        # V16.1: push2 扩展字段（2026-08-04 官方 TdxQuant 交叉验证）
        # ─────────────────────────────────────────────
        # 涨停/跌停价（f51/f52，官方 ZTPrice/DTPrice 精确匹配）
        for src, dst in [("f51", "limit_up"), ("f52", "limit_down")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # EPS/BPS（f55/f92，与东财 F10 精确匹配）
        for src, dst in [("f55", "eps"), ("f92", "bps")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 股息率（f126，官方 DYRatio 匹配）
        v = data.get("f126")
        if v is not None and v != "-":
            try:
                result["dividend_yield"] = float(v)
            except (TypeError, ValueError):
                pass

        # PE 三口径 + PB（🔴2026-09-01 据 field_dict 定案纠正：f162=动态PE/f163=静态PE(LYR)/f164=TTM(pe_ttm)/f167=PB）
        pe_map = {
            "f162": "pe_dynamic",
            "f163": "pe_lyr",
            "f164": "pe_ttm",
            "f167": "pb",
        }
        for src, dst in pe_map.items():
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 52周高低（f174/f175，官方 HisHigh/HisLow 精确匹配）
        for src, dst in [("f174", "high_52w"), ("f175", "low_52w")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 行业板块代码（f198，如 BK1277）
        v = data.get("f198")
        if v and isinstance(v, str):
            result["industry_code_push2"] = v

        # V16.2: 最新报告期（f221，YYYYMMDD）
        v = data.get("f221")
        if v and str(v).strip() and str(v).strip() != "-":
            result["report_period"] = str(v).strip()

        # 交易时段数组（f80，JSON 字符串 → 原样保留）
        v = data.get("f80")
        if v and isinstance(v, str):
            try:
                result["trading_periods"] = json.loads(v)
            except (TypeError, ValueError, json.JSONDecodeError):
                result["trading_periods"] = []

        # 资金流字段(f135-f146 + f149)——V17.0.16(2026-08-31) 结构实证**重定案**
        #
        # ⚠️ 旧版(V17.0)把 f135-f146 当成**并列的四档** 特大/大单/中单/小单，并算
        #    「主力净额 = f137 + f140」——**错的**，本段已按实证重写。
        #
        # 三条独立铁证（详见 docs/field_dict.md §12.3.3）：
        #   ① 结构自洽 + 全组合盲搜（12 采集日 169 样本，相对差 **0.00**，100% 命中）：
        #        f135 = f138 + f141     f136 = f139 + f142     f137 = f140 + f143
        #      → **f137 是合计档**，不可能是并列的"特大单净"。
        #        旧命名下应推出 f137 = f138 − f139 = f140，但实测 0/169 相等（96.4% 显著分离）。
        #   ② ulist239 同名号段（12 采集日 236 样本）：**f62 == f66 + f72 命中 236/236 = 100%**
        #      → 东财标准档位：f62=主力净、f66=超大单净、f72=大单净、f78=中单净、f84=小单净。
        #   ③ 跨接口对撞（234 样本，2% 容差）：
        #        f62==f137 96.6%   f66==f140 98.3%   f72==f143 96.2%
        #        f78==f146 95.7%   f84==f149 96.2%   f84==f146 仅 0.9%（排除）
        #
        # 正确层级（买/卖/净 三组 + 主力为合计）：
        #      f138/139/140 = 超大单 买/卖/净
        #      f141/142/143 = 大单   买/卖/净
        #      f135/136/137 = **主力** 买/卖/净  （= 超大单 + 大单，东财官方"主力"定义）
        #      f144/145/146 = 中单   买/卖/净
        #      f149         = 小单净（**f135-f146 段内没有小单买/卖明细**）
        #
        # 后果（旧 bug 的实际影响）：`主力净 = f137 + f140` 把超大单净**重复计一次**，
        #   实测 (f137+f140)/f137 中位 **1.196** → 主力净额虚高约 **40%**，
        #   并沿 data_provider `main_net_buy_amount` 流入各报告章节（静默、不报错）。
        #   现改为**直接取 f137**，不再相加。
        #
        # 单位: 元
        flow_map = {
            "f135": ("fund_main_buy", "fund_flow"),      # 主力买入额 = f138 + f141
            "f136": ("fund_main_sell", "fund_flow"),     # 主力卖出额 = f139 + f142
            "f137": ("fund_main_today", "fund_flow"),    # 主力净额   = f140 + f143（**不可再加 f140**）
            "f138": ("fund_super_buy", "fund_flow"),     # 超大单买入额
            "f139": ("fund_super_sell", "fund_flow"),    # 超大单卖出额
            "f140": ("fund_super_today", "fund_flow"),   # 超大单净额
            "f141": ("fund_large_buy", "fund_flow"),     # 大单买入额
            "f142": ("fund_large_sell", "fund_flow"),    # 大单卖出额
            "f143": ("fund_large_today", "fund_flow"),   # 大单净额
            "f144": ("fund_mid_buy", "fund_flow"),       # 中单买入额
            "f145": ("fund_mid_sell", "fund_flow"),      # 中单卖出额
            "f146": ("fund_mid_today", "fund_flow"),     # 中单净额
            "f149": ("fund_small_today", "fund_flow"),   # 小单净额（无买/卖明细）
        }
        for src, (dst, _cat) in flow_map.items():
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # V17.0.16: 主力净额**直接等于 f137**（东财已聚合好 超大单 + 大单）。
        # 旧版在此外加 f140 属重复计数，见上方 flow_map 注释的三条铁证。

        # 近5日主力净流入数组（f178，JSON）
        v = data.get("f178")
        if v and isinstance(v, str):
            try:
                result["fund_5d_array"] = json.loads(v)
                # V17.0: 5日主力净由 f178 数组聚合(替代原 f141 误读)
                _s5 = sum(float(x.get("mainNetAmt", 0)) for x in result["fund_5d_array"] if isinstance(x, dict))
                if _s5:
                    result["fund_main_5d"] = _s5
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

        # V17.0.7(2026-08-25 字典终破): 财务 TTM 族(单位见键注释; 口径经
        # fuyao 官方三大报表 5/5 终判 + 报告期切换动态双证——详见
        # docs/field_verification/20260825_cross_analysis.md)
        for src, dst in [
            ("f103", "ocf_ttm"),            # 经营活动现金流量净额 TTM (元)
            ("f104", "revenue_ttm"),        # 营业总收入 TTM (元)
            ("f105", "net_profit_period"),  # 归母净利润 最新报告期 (元)
            ("f108", "eps_deduct_ttm"),     # 扣非每股收益 TTM (元/股)
            ("f109", "net_profit_annual"),  # 归母净利润 最新年报 (元)
            ("f160", "eps_annual"),         # 年报EPS (=f109/f84) (元/股)
            ("f190", "undist_profit_ps"),   # 每股未分配利润 (元/股, ≡ulist f48)
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        result["data_date"] = datetime.now().strftime("%Y-%m-%d")
        return result
    except Exception as _e:
        _debug_log(f"sc_datasource get_em_quote_full ({code}): {_e}")
        return {}

def eastmoney_stock_info_push2(code: str) -> Dict[str, Any]:
    """东财 push2 个股基本面信息（含上市日期 f189，不走 TDX）。

    当 TDX 无法获取 list_date 时作为 fallback。
    返回: {code, name, industry, total_shares, float_shares, mcap, float_mcap, list_date}
    """
    market_code = 1 if em_secid_prefix(code) == "1." else 0  # V17.0 S3: 统一(含北交所 92)
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
        "secid": f"{market_code}.{code}",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        if r is None:
            return {}
        d = r.json().get("data", {})
        return {
            "code": d.get("f57", ""),
            "name": d.get("f58", ""),
            "industry": d.get("f127", ""),
            "total_shares": d.get("f84", 0),
            "float_shares": d.get("f85", 0),
            "mcap": d.get("f116", 0),
            "float_mcap": d.get("f117", 0),
            "list_date": str(d.get("f189", "")),
            "price": d.get("f43", 0),
        }
    except Exception as _e:
        _debug_log(f"datasource eastmoney_stock_info_push2 ({code}): {_e}")
        return {}

def _em_fflow_request(path: str, params: Dict[str, Any], timeout: int = 10, prefer_his: bool = False):
    """V16.2.4: 依次尝试 _FFLOW_HOSTS，返回首个非 None 的 Response（含 403/429 语义由 em_get 处理）。
    V17.0.4(2026-08-19): prefer_his=True(历史资金流) → push2his 全窗口优先——
    原顺序 push2delay 第 1(为 lmt=1 实时设计) 会把 daykline 历史请求截断成单日(8/18 全仓 sht 60日资金流仅 1 天根因)。
    """
    import random as _rand

    _hosts = list(_FFLOW_HOSTS)
    if prefer_his:
        _his = "push2his.eastmoney.com"
        _hosts = [_his] + [h for h in _hosts if h != _his]
    else:
        _rand.shuffle(_hosts[0:2])  # 前两域随机轮换（防固定域持续触发风控）
    for _h in _hosts:
        try:
            _r = em_get(f"https://{_h}{path}", params=params, headers={"User-Agent": UA}, timeout=timeout)
            if _r is not None:
                return _r
        except Exception as _e:
            _debug_log(f"datasource fflow host {_h} error: {type(_e).__name__} {str(_e)[:60]}")
    return None

def get_em_fund_flow(code: str) -> Dict[str, Any]:
    """V12.0: 获取个股实时资金流（替代 TDX get_fund_flow）。

    ⚠️ V17.0.13 口径（easy_tdx #55，2026-08-30）：本项目主力净额统一用东财
    fflow 口径（与 push2 f137+f140 / thsdk 一致）。**严禁**改用 easy_tdx 原生
    get_fund_flow（0x0fb5 逐笔聚合，与东财/同花顺主力净流入重合度仅 ~14%，不可比）。

    使用东财 fflow daykline 接口，取最新一天的数据（即当日实时累计）。
    V16.2.4 修复: push2/push2his 域连接级风控时自动切 push2delay 延时镜像域
    （延时 15 分钟，盘后一致；风控面独立）。

    Returns:
        dict: {"main_net": float, "main_net_wan": float, "total_net": float,
               "super_in": float, "super_out": float,
               "large_in": float, "large_out": float,
               "medium_in": float, "medium_out": float,
               "small_in": float, "small_out": float}
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": "1",  # 只取最新一天
        "klt": "101",  # 日K线
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        r = _em_fflow_request("/api/qt/stock/fflow/daykline/get", params)
        if r is None:
            return {}
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return {}
        # klines 格式: "日期,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入"
        parts = klines[-1].split(",")
        if len(parts) < 6:
            return {}
        main_net = _safe_float(parts[1])
        small_net = _safe_float(parts[2])
        medium_net = _safe_float(parts[3])
        large_net = _safe_float(parts[4])
        super_net = _safe_float(parts[5])
        # 东财返回净额，TDX格式需要 in/out 分开
        # 转换规则：净额>0时in=净额,out=0；净额<0时in=0,out=|净额|
        return {
            "main_net": main_net,
            "main_net_wan": main_net / 10000.0,
            # 东财定义"主力净流入 = 大单净流入 + 超大单净流入"(见本函数 klines 格式注释)，
            # 故 total_net 应为主力+小单+中单，大单/超大单已被主力包含；原五档全加会把大/超重复计。
            # （原 V16.2 注释"漏大单/超大单"为误解，2026-08-30 修；如需实盘复核：
            # 取任一标的对比 main_net 与 large_net+super_net 是否相等）
            "total_net": main_net + small_net + medium_net,
            "super_in": max(super_net, 0),
            "super_out": max(-super_net, 0),
            "large_in": max(large_net, 0),
            "large_out": max(-large_net, 0),
            "medium_in": max(medium_net, 0),
            "medium_out": max(-medium_net, 0),
            "small_in": max(small_net, 0),
            "small_out": max(-small_net, 0),
        }
    except Exception as _e:
        _debug_log(f"datasource get_em_fund_flow ({code}): {_e}")
        return {}

def get_em_history_fund_flow(code: str, days: int = 120) -> List[Dict[str, Any]]:
    """V12.0: 获取个股历史资金流（替代 TDX get_history_fund_flow）。

    ⚠️ V17.0.13 口径（easy_tdx #55，2026-08-30）：沿用东财 fflow 口径，与
    get_em_fund_flow / push2 f137+f140 一致。勿回退 easy_tdx 原生历史资金流
    （0x0fb5 逐笔聚合，与东财/同花顺主力净流入不可比）。

    使用东财 push2 fflow daykline 接口，取最近 N 天的日级数据。

    Args:
        code: 股票代码
        days: 返回天数

    Returns:
        list: [{"date": str, "main_net": float, "super_net": float,
                "large_net": float, "mid_net": float, "small_net": float}, ...]
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": str(max(days, 1)),
        "klt": "101",  # 日K线
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        # V16.2.4: 多域轮换（push2his 全窗口 → push2 → push2delay 单日保底）
        # V17.0.4(2026-08-19): prefer_his=True 历史资金流优先 push2his 全窗口
        # (原顺序 push2delay 第 1 会把历史请求截断成单日——8/18 全仓 60日资金流仅 1 天根因)
        r = _em_fflow_request("/api/qt/stock/fflow/daykline/get", params, prefer_his=True)
        if r is None:
            return []
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return []
        rows = []
        for line in klines:
            parts = line.split(",")
            if len(parts) < 6:
                continue
            main_net = _safe_float(parts[1])
            small_net = _safe_float(parts[2])
            medium_net = _safe_float(parts[3])
            large_net = _safe_float(parts[4])
            super_net = _safe_float(parts[5])
            date_str = str(parts[0])[:10]
            rows.append(
                {
                    "date": date_str,
                    "main_net": main_net,
                    "super_net": super_net,
                    "large_net": large_net,
                    "mid_net": medium_net,
                    "small_net": small_net,
                }
            )
        # 按日期降序（最新在前），与原 TDX 行为保持一致
        rows.sort(key=lambda x: x["date"], reverse=True)
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_em_history_fund_flow ({code}): {_e}")
        return []
