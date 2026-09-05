"""stock_common/sc_datasource/_holders.py — V17.1 拆包子模块（Facade 重导出，零行为变化）"""
from ._shared import *  # 取得 import 块名 + 常量（含私有，见 _shared.__all__）

def _holder_fetch_from_sqlite(code: str) -> Optional[Dict[str, Any]]:
    """从 SQLite 获取股东户数数据。"""
    try:
        from core.stock_cache import get_cache

        cache_key = f"holder_data:{code}"
        cached_data = get_cache("holder", "holder_data", cache_key)
        if cached_data:
            return cached_data
    except Exception as _e:
        _debug_log(f"datasource holder fetch sqlite error: {_e}")
    return None

def _holder_update_sqlite(code: str, records: List[Dict[str, Any]], timestamp: float) -> None:
    """更新 SQLite 中的股东户数数据。"""
    try:
        from core.stock_cache import set_cache

        cache_key = f"holder_data:{code}"
        data = {"records": records, "updated": timestamp}
        # 使用 holder_cache 的 TTL（60天）
        set_cache("holder", "holder_data", data, _HOLDER_CACHE_TTL, cache_key)
    except Exception as _e:
        _debug_log(f"datasource holder update sqlite error: {_e}")

def _holder_fetch_em(code: str, page_size: int) -> List[Dict[str, Any]]:
    """从东财获取股东户数 → 按日期升序的 records 列表。"""
    data = _em_filter(
        code, "RPT_F10_EH_HOLDERNUM", page_size=page_size, sort_columns="END_DATE", sort_types="-1"
    )
    if not data:
        return []
    records = []
    for r in data:
        records.append(
            {
                "date": str(r.get("END_DATE", ""))[:10],
                "holder_num": int(r.get("HOLDER_TOTAL_NUM") or 0),
                "avg_shares": _safe_float(r.get("AVG_FREE_SHARES")),
            }
        )
    records.sort(key=lambda x: x["date"])
    return records

def _holder_fetch_tdx_optimized(code: str, records: List[Dict[str, Any]], now: float) -> bool:
    """从 TDX 拿最新 1 期，去重后追加到 records（优化版：直接更新 SQLite）。"""
    from core.tdx_client import _get_tdx_client

    client = _get_tdx_client()
    if client is None:
        return False
    info = client.get_finance_info(1 if code.startswith("6") else 0, code)
    if info is None or info.empty:
        return False
    # V15.1: 修正股东户数 key（参考 docs/field_dict.md 第 7 章）
    # 正确 key: gudongrenshu（无下划线）
    hnum = int(info.iloc[0].get('gudongrenshu', 0))
    upd = str(int(info.iloc[0].get('updated_date', 0)))
    if hnum <= 0:
        return False
    date_str = f"{upd[:4]}-{upd[4:6]}-{upd[6:8]}" if len(upd) == 8 else ""
    if not records or records[-1].get("holder_num") != hnum:
        records.append({"date": date_str, "holder_num": hnum})
        if len(records) > 10:
            records = records[-10:]
        _holder_update_sqlite(code, records, now)
        return True
    return False

def _holder_fetch_tdx(code: str, records: List[Dict[str, Any]], now: float) -> bool:
    """从 TDX 拿最新 1 期，去重后追加到 records（保持向后兼容）。"""
    return _holder_fetch_tdx_optimized(code, records, now)

def holder_change(code: str, local_only: bool = False) -> List[Dict[str, Any]]:
    """获取股东户数多期变化（优化版：直接使用 SQLite）。

    逻辑：
      - 缓存新鲜 < 60 天 → 直接返回
      - 缓存为空 → F10 优先（多期）→ 东财 10 期兜底
      - 缓存过期 ≥ 60 天且 < 90 天 → TDX 追加 1 期（同季度增量）
      - 缓存过期 ≥ 90 天 → F10 优先 → 东财 5 期兜底

    返回: [{date, holder_num, change_num, change_ratio, avg_shares}, ...] 最新在前

    V17.0(2026-08-15) H6 修复: 新增 local_only——缓存未命中时直接返回 []
    （val 策略23 全市场扫描禁逐股网络请求, 仅缓存命中判筹码集中）。
    """
    from core.stock_cache import get_cache, set_cache, TTL

    # 尝试从缓存获取
    cache_key = f"holder_data:{code}"
    cached_data = get_cache("holder", "holder_change", cache_key)

    if cached_data is not None:
        return cached_data
    if local_only:
        return []

    # 缓存未命中，重新获取数据
    now = time.time()

    # 尝试从 SQLite 获取现有记录
    existing_data = _holder_fetch_from_sqlite(code)
    if existing_data:
        records = existing_data.get("records", [])
        updated = existing_data.get("updated", 0)
        age = now - updated

        # ① 缓存新鲜 < 60 天 → 直接返回
        if age < _HOLDER_CACHE_TTL:
            return _compute_holder_changes(records)

        # ② 缓存过期 ≥ 90 天 → F10 优先 → 东财 5 期兜底（跨季度补全）
        if age >= _HOLDER_CACHE_REFRESH:
            # V9.0: F10 优先（76+ 期，远多于东财 5 期）
            f10_records = _holder_fetch_f10(code)
            if f10_records:
                _holder_update_sqlite(code, f10_records, now)
                return _compute_holder_changes(f10_records)
            records = _holder_fetch_em(code, 5)
            if records:
                _holder_update_sqlite(code, records, now)
                return _compute_holder_changes(records)
    else:
        records = []

    # ③ 缓存为空 → F10 优先 → 东财 10 期兜底（首次初始化）
    if not records:
        # V9.0: F10 优先（一次拿全所有历史期数）
        f10_records = _holder_fetch_f10(code)
        if f10_records:
            _holder_update_sqlite(code, f10_records, now)
            return _compute_holder_changes(f10_records)
        records = _holder_fetch_em(code, 10)
        if records:
            _holder_update_sqlite(code, records, now)
            return _compute_holder_changes(records)

    # ④ 尝试从 SQLite 获取现有记录（如果还没有的话）
    if not records:
        existing_data = _holder_fetch_from_sqlite(code)
        if existing_data:
            records = existing_data.get("records", [])

    # ⑤ 缓存过期 ≥ 60 天且 < 90 天 → TDX 追加 1 期
    if _holder_fetch_tdx_optimized(code, records, now):
        return _compute_holder_changes(records)

    # ⑥ 全部失败 → 返回现有记录
    return _compute_holder_changes(records)

def _holder_fetch_f10(code: str) -> List[Dict[str, Any]]:
    """V9.0: 从 F10 股东研究获取股东户数多期记录。

    F10 holder_count 通常包含 76+ 期历史数据，远多于东财 10 期。
    字段映射：F10 entry (period + 股东人数(户) + 人均流通股(股) + etc.) → records [{date, holder_num, avg_shares}]
    """
    try:
        from core.tdx_client import tdx_get_shareholder_research

        f10 = tdx_get_shareholder_research(code)
        if not f10:
            return []
        holder_count = f10.get('holder_count', [])
        if not holder_count:
            return []
        records: List[Dict[str, Any]] = []
        for entry in holder_count:
            period = (entry.get('period', '') or '').strip()
            if not period:
                continue
            # F10 字段名带后缀，如 "股东人数(户)"、"人均流通股(股)"
            # 用 startswith 匹配，兼容不同后缀
            holder_num = 0
            for k, v in entry.items():
                if k.startswith('股东人数') or k.startswith('股东户数') or k == '户数':
                    holder_num = int(_safe_float(v or 0))
                    break
            if holder_num <= 0:
                continue
            avg_shares = 0.0
            for k, v in entry.items():
                if (
                    k.startswith('人均流通股')
                    or k.startswith('户均持股')
                    or k.startswith('户均流通股')
                    or k.startswith('人均持股')
                ):
                    avg_shares = _safe_float(v or 0)
                    break
            records.append(
                {
                    "date": str(period)[:10],
                    "holder_num": holder_num,
                    "avg_shares": avg_shares,
                }
            )
        # 按日期升序（_compute_holder_changes 内部会 reverse）
        records.sort(key=lambda x: x["date"])
        return records
    except Exception as _e:
        _debug_log(f"datasource holder_change ({code}): {_e}")
        return []

async def holder_change_async(session, code: str) -> List[Dict[str, Any]]:
    """async 版：股东户数多期变化（代理到同步版）。"""
    return await asyncio.to_thread(holder_change, code)

def _compute_holder_changes(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """从原始记录列表计算环比变化。"""
    if not records:
        return []
    result = []
    for i in range(len(records)):
        r = records[i]
        prev_num = records[i - 1]["holder_num"] if i > 0 else 0
        change_num = r["holder_num"] - prev_num if i > 0 and prev_num > 0 else 0
        change_ratio = round(change_num / prev_num * 100, 2) if i > 0 and prev_num > 0 else 0.0
        result.append(
            {
                "date": r["date"],
                "holder_num": r["holder_num"],
                "change_num": change_num,
                "change_ratio": change_ratio,
                "avg_shares": r.get("avg_shares", 0),
            }
        )
    # 最新在前
    result.reverse()
    return result

def _cninfo_get_orgid(code: str) -> str:
    """动态查询巨潮公告的 orgId（SKILL.md V3.2.2 推荐）。

    优先从缓存获取，缓存未命中时先尝试动态查询官方映射表，
    失败则使用硬编码fallback。

    Args:
        code: 股票代码

    Returns:
        orgId 字符串
    """
    # 先查缓存
    if code in _CNINFO_ORGID_CACHE:
        return _CNINFO_ORGID_CACHE[code]

    # 硬编码 fallback（用于动态查询失败时）
    # 市场前缀 → cninfo orgId 前缀：
    #   6xxxxx(沪市主板/科创板) → gssh0
    #   8xxxxx/4xxxxx/92xxxx(北交所) → gsbj0
    #   0xxxxx/3xxxxx(深市) → gssz0
    # M10 修复：原代码把 92x(北交所新代码段) 落入 else 得 gssz0(深市)，单位/主体错乱；
    # 现归入北交所分支。
    if code.startswith("6"):
        fallback = f"gssh0{code}"
    elif code.startswith("8") or code.startswith("4") or code.startswith("92"):
        fallback = f"gsbj0{code}"
    else:
        fallback = f"gssz0{code}"

    # 尝试动态查询（SKILL.md V3.2.2 推荐方案）
    # M10 修复：原仅查 szse(深市) 列表，沪/北交所代码恒查不到 → 恒走错误 fallback。
    # 现按市场补充 shse(沪市) 列表，任一命中即返回真实 orgId。
    _cninfo_json_candidates = [
        "https://www.cninfo.com.cn/new/data/szse_stock.json",
        "https://www.cninfo.com.cn/new/data/shse_stock.json",
    ]
    for url in _cninfo_json_candidates:
        try:
            r = _quick_request(url, timeout=10)
            if r is not None:
                data = r.json()
                for item in data:
                    if item.get("code") == code:
                        orgid = item.get("orgId", fallback)
                        _CNINFO_ORGID_CACHE[code] = orgid
                        return orgid
        except Exception as _e:
            _debug_log(f"datasource cninfo orgid query error ({url}): {_e}")

    # 动态查询失败，返回硬编码 fallback
    _CNINFO_ORGID_CACHE[code] = fallback
    return fallback

def get_strategic_announcements(
    code: str, page_size: int = 50, days: Optional[int] = None,
    importance_filter: bool = False, keywords: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """巨潮公告查询 → orgId → searchkey → TDX F10 三层兜底（SKILL.md V3.2.2 增强：动态orgId查询）。

    Args:
        code: 股票代码
        page_size: 返回数量上限
        days: 限定最近 N 天，None=不限（长线），30=中线，7=短线
        importance_filter: V7.5新增，是否仅返回重要公告（True=仅重要，False=全部）
        keywords: V17.0 S4 新增——自定义关键词过滤（覆盖默认列表；mak 异动公告用 ["异常波动"]）
    返回: [{title, date, type, is_important}, ...]
    """
    # 计算日期范围
    sd_str = ""
    if days:
        sd_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        td_str = datetime.now().strftime("%Y-%m-%d")
        se_date = f"{sd_str}~{td_str}"
    else:
        se_date = ""

    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"

    # SKILL.md V3.2.2 推荐：先尝试动态查询orgId，失败则用硬编码fallback
    ext_org_id = _cninfo_get_orgid(code)

    payload = {
        "orgId": ext_org_id,
        "stock": f"{code},{ext_org_id}",
        "tabName": "fulltext",
        "pageSize": str(page_size),
        "pageNum": "1",
        "column": "",
        "category": "",
        "plate": "",
        "seDate": se_date,
        "searchkey": "",
        "secid": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.cninfo.com.cn/new/disclosure",
    }
    _cfg = _load_settings()
    if keywords is None:
        keywords = _cfg.get(
            "announcement_keywords",
            [
                "回购",
                "增持",
                "减持",
                "年报",
                "分红",
                "派息",
                "激励",
                "员工持股",
                "战略合作",
                "业绩预告",
                "中标",
                "立案",
                "合同",
                "收购",
                "股权转让",
                "异动",
                "严重异动",
            ],
        )
    _noise = _cfg.get("announcement_noise", ["摘要", "提示性", "英文版"])
    _importance_kw = _cfg.get("announcement_importance_keywords", [])
    try:
        r = _quick_request(url, data=payload, headers=headers, method="POST", timeout=15)
        anns = []
        if r is not None:
            d = r.json()
            anns = d.get("announcements", []) or []
        if not anns:
            # orgId 失败 → searchkey 兜底
            payload2 = {
                "orgId": "",
                "stock": "",
                "tabName": "fulltext",
                "pageSize": str(page_size),
                "pageNum": "1",
                "column": "",
                "category": "",
                "plate": "",
                "seDate": se_date,
                "searchkey": str(code),
                "secid": "",
                "sortName": "",
                "sortType": "",
                "isHLtitle": "true",
            }
            r2 = _quick_request(url, data=payload2, headers=headers, method="POST", timeout=15)
            if r2 is not None:
                d2 = r2.json()
                anns2 = d2.get("announcements", []) or []
                if anns2:
                    anns = anns2
        if not anns:
            # 巨潮双路径均失败 → TDX F10 兜底
            try:
                from core.tdx_client import tdx_get_latest_announcements

                tdx_anns = tdx_get_latest_announcements(code, days=7)
                if tdx_anns:
                    anns = [
                        {
                            "announcementTitle": a["title"],
                            "announcementTime": (
                                int(datetime.strptime(a["date"], "%Y-%m-%d").timestamp() * 1000)
                                if a.get("date")
                                else 0
                            ),
                        }
                        for a in tdx_anns
                    ]
            except Exception as _e:
                _debug_log(f"datasource tdx announcements fallback error: {_e}")
        rows = []
        for item in anns:
            _sc = str(item.get("secCode", ""))
            if _sc and _sc != str(code):
                continue
            title = item.get("announcementTitle", "")
            title = re.sub(r'<[^>]+>', '', title)
            if any(k in title for k in keywords) and not any(noise in title for noise in _noise):
                ts = item.get("announcementTime", 0)
                if isinstance(ts, (int, float)) and ts > 1000000000000:
                    date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                else:
                    date_str = str(ts)[:10]
                # V7.5新增：重要等级标记
                is_important = any(imp_k in title for imp_k in _importance_kw)
                # 如果开启重要过滤且不是重要公告，跳过
                if importance_filter and not is_important:
                    continue
                rows.append(
                    {
                        "title": title,
                        "date": date_str,
                        "type": item.get("announcementTypeName", "") or "",
                        "is_important": is_important,
                        # V16.1: 保留 PDF 直链/公告 ID（sht/med/lng 可下附件）
                        "adjunct_url": item.get("adjunctUrl", "") or "",
                        "announcement_id": item.get("announcementId", "") or "",
                    }
                )
        return rows
    except Exception as _e:
        _debug_log(f"datasource strategic_announcements ({code}): {_e}")
        return []

async def get_strategic_announcements_async(
    session, code: str, page_size: int = 50, days: Optional[int] = None
) -> List[Dict[str, Any]]:
    """async 版：巨潮公告查询

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
          TDX F10 兜底保留 asyncio.to_thread。
    """
    from datetime import datetime, timedelta

    _cfg = _load_settings()
    keywords = _cfg.get("announcement_keywords", [])
    _noise = _cfg.get("announcement_noise", ["摘要", "提示性", "英文版"])
    _importance_kw = _cfg.get("announcement_importance_keywords", [])

    if days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        se_date = f"{start_date.strftime('%Y-%m-%d')}~{end_date.strftime('%Y-%m-%d')}"
    else:
        se_date = ""

    importance_filter = bool(_cfg.get("strategy_announcement_importance_filter", False))

    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    headers = {
        "User-Agent": UA,
        "Referer": "http://www.cninfo.com.cn/",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
    }

    try:
        payload = {
            "orgId": "",
            "stock": str(code),
            "tabName": "fulltext",
            "pageSize": str(page_size),
            "pageNum": "1",
            "column": "",
            "category": "",
            "plate": "",
            "seDate": se_date,
            "searchkey": "",
            "secid": "",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }
        d = await _async_quick_request(
            session, url, data=payload, headers=headers, method="POST", timeout=15
        )
        anns = []
        if d is not None:
            anns = d.get("announcements", []) or []

        if not anns:
            payload2 = {
                "orgId": "",
                "stock": "",
                "tabName": "fulltext",
                "pageSize": str(page_size),
                "pageNum": "1",
                "column": "",
                "category": "",
                "plate": "",
                "seDate": se_date,
                "searchkey": str(code),
                "secid": "",
                "sortName": "",
                "sortType": "",
                "isHLtitle": "true",
            }
            d2 = await _async_quick_request(
                session, url, data=payload2, headers=headers, method="POST", timeout=15
            )
            if d2 is not None:
                anns2 = d2.get("announcements", []) or []
                if anns2:
                    anns = anns2

        if not anns:
            try:
                import asyncio
                from core.tdx_client import tdx_get_latest_announcements

                tdx_anns = await asyncio.to_thread(tdx_get_latest_announcements, code, days=7)
                if tdx_anns:
                    anns = [
                        {
                            "announcementTitle": a["title"],
                            "announcementTime": (
                                int(datetime.strptime(a["date"], "%Y-%m-%d").timestamp() * 1000)
                                if a.get("date")
                                else 0
                            ),
                        }
                        for a in tdx_anns
                    ]
            except Exception as _e:
                _debug_log(f"datasource tdx announcements fallback async error: {_e}")

        rows = []
        for item in anns:
            _sc = str(item.get("secCode", ""))
            if _sc and _sc != str(code):
                continue
            title = item.get("announcementTitle", "")
            title = re.sub(r'<[^>]+>', '', title)
            if any(k in title for k in keywords) and not any(noise in title for noise in _noise):
                ts = item.get("announcementTime", 0)
                if isinstance(ts, (int, float)) and ts > 1000000000000:
                    date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                else:
                    date_str = str(ts)[:10]
                is_important = any(imp_k in title for imp_k in _importance_kw)
                if importance_filter and not is_important:
                    continue
                rows.append(
                    {
                        "title": title,
                        "date": date_str,
                        "type": item.get("announcementTypeName", "") or "",
                        "is_important": is_important,
                        # V16.1: 保留 PDF 直链/公告 ID
                        "adjunct_url": item.get("adjunctUrl", "") or "",
                        "announcement_id": item.get("announcementId", "") or "",
                    }
                )
        return rows
    except Exception as _e:
        _debug_log(f"datasource strategic_announcements_async ({code}): {_e}")
        return []

def get_holder_structure(code: str) -> List[Dict[str, Any]]:
    """东财 RPT_F10_EH_HOLDERS → 多季度十大流通股东分类统计。
    模块级缓存，同一脚本运行期内不重复调 API。

    返回: [{date, total, northbound, foreign, foreign_count,
            domestic, domestic_count, individual, individual_count}, ...] 最新在前

    V9.1: 移除 F10 优先逻辑（F10 缺持股比例字段，机构持股计算为 0）。
    """
    if code in _holder_structure_cache:
        return _holder_structure_cache[code]

    # V9.1: 已移除 F10 优先逻辑（F10 缺持股比例字段，机构持股计算为 0）

    # 东财 HTTP
    data = eastmoney_datacenter(
        code,
        "RPT_F10_EH_HOLDERS",
        columns="END_DATE,HOLDER_NAME,HOLD_NUM_RATIO",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=50,
        sort_columns="END_DATE",
        sort_types="-1",
    )
    if not data:
        return []

    # 按报告期分组
    periods = {}
    for h in data:
        ed = str(h.get("END_DATE", ""))[:10]
        if ed not in periods:
            periods[ed] = []
        periods[ed].append(h)

    result = []
    for date_key in sorted(periods.keys(), reverse=True)[:4]:
        holders = periods[date_key]
        nb = fe = dm = ind = 0.0
        fc = dc = ic = 0
        dm_tags = {"国资": 0.0, "证金汇金": 0.0, "公募": 0.0, "险资": 0.0, "社保": 0.0}

        for h in holders[:10]:
            name = (h.get("HOLDER_NAME", "") or "").strip()
            ratio = float(h.get("HOLD_NUM_RATIO", 0))
            has_cn = any('\u4e00' <= c <= '\u9fff' for c in name)
            has_en = any(c.isalpha() and ord(c) < 128 for c in name)

            if '香港中央结算' in name or 'HKSCC' in name.upper():
                nb += ratio
            elif not has_cn and has_en:
                fe += ratio
                fc += 1
            elif (
                has_cn
                and len([c for c in name if '\u4e00' <= c <= '\u9fff']) <= 3
                and not any(
                    kw in name
                    for kw in [
                        '公司',
                        '基金',
                        '保险',
                        '银行',
                        '信托',
                        '证券',
                        '合伙',
                        '集团',
                        '投资',
                        '控股',
                    ]
                )
            ):
                ind += ratio
                ic += 1
            else:
                dm += ratio
                dc += 1
                # 境内机构细分
                if '社保' in name:
                    dm_tags["社保"] += ratio
                elif '保险' in name:
                    dm_tags["险资"] += ratio
                elif '中国证券金融' in name or '中央汇金' in name:
                    dm_tags["证金汇金"] += ratio
                elif '基金' in name:
                    dm_tags["公募"] += ratio
                elif '集团' in name or '国有' in name or '国资委' in name:
                    dm_tags["国资"] += ratio

        result.append(
            {
                "date": date_key,
                "total": round(nb + fe + dm + ind, 1),
                "northbound": round(nb, 2),
                "foreign": round(fe, 1),
                "foreign_count": fc,
                "domestic": round(dm, 1),
                "domestic_count": dc,
                "individual": round(ind, 1),
                "individual_count": ic,
                "dm_detail": {k: round(v, 1) for k, v in dm_tags.items() if v > 0},
            }
        )

    _holder_structure_cache[code] = result
    return result

async def get_holder_structure_async(
    session: Any, code: str, today_str: str = ""
) -> Dict[str, Any]:
    """异步版 get_holder_structure"""
    import asyncio

    return await asyncio.to_thread(get_holder_structure, code)

def cninfo_irm(code: str, page_size: int = 30, page_num: int = 1) -> List[Dict[str, Any]]:
    """互动易问答（深沪统一走巨潮）。

    V9.6 新增：两步调用——先获取orgId，再获取问答列表。
    参数放query string（POST但body空），否则400。

    Args:
        code: 6位股票代码
        page_size: 每页条数，默认30
        page_num: 页码，默认1

    Returns:
        问答列表，包含 question/answer/ask_time/answerer 字段
    """
    from datetime import datetime
    import requests

    # V16.2.3: 巨潮互动易无统一入口（交易所直连），加进程级礼貌限速（每次调用 2 个请求）
    try:
        from stock_common.sc_network import _gen_wait_process_interval
        _gen_wait_process_interval()
    except Exception:
        pass
    try:
        # V16.3 O14: 巨潮互动易强制直连（忽略系统代理——GD 外全部直连）
        _no_proxy = {"http": None, "https": None}
        r1 = requests.post(
            "https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo",
            data={"keyWord": code},
            headers={"User-Agent": UA},
            timeout=10,
            proxies=_no_proxy,
        )
        d1 = r1.json().get("data") or []
        if not d1:
            return []
        org_id = d1[0].get("secid")

        params = {
            "_t": 1,
            "stockcode": code,
            "orgId": org_id,
            "pageSize": page_size,
            "pageNum": page_num,
            "keyWord": "",
            "startDay": "",
            "endDay": "",
        }
        r2 = requests.post(
            "https://irm.cninfo.com.cn/newircs/company/question",
            params=params,
            headers={"User-Agent": UA},
            timeout=10,
            proxies=_no_proxy,
        )
        rows = r2.json().get("rows") or []

        out = []
        for it in rows:
            pd = it.get("pubDate")
            out.append(
                {
                    "code": it.get("stockCode"),
                    "company": it.get("companyShortName"),
                    "question": it.get("mainContent"),
                    "answer": it.get("attachedContent"),
                    "answerer": it.get("attachedAuthor"),
                    "ask_time": (
                        datetime.fromtimestamp(pd / 1000).strftime("%Y-%m-%d %H:%M") if pd else ""
                    ),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource cninfo_irm ({code}): {_e}")
        return []
