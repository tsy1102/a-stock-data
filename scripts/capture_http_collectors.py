"""Public HTTP and Eastmoney source collectors used by daily capture.

The daily entry point injects patchable policy constants and diagnostics; all
HTTP sessions, throttles, ban state, and retries remain in stock_common.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass(frozen=True)
class CaptureHttpDependencies:
    em_full_fields: Any
    request_failure_summary: Callable[..., Any]
    request_is_rate_limited: Callable[..., bool]
    em_secid_prefix: Callable[..., str]
    sina_captured_field_codes: Any
    sina_paused_option_fields: Any
    sina_required_flow_fields: Any
    sina_unresolved_field_codes: Any
    baidu_pending_field_codes: Any
    parse_baidu_kline_probe: Callable[..., Any]
    last_completed_trading_day: Callable[..., Any]
    em_capture_pause_reason: Callable[..., Any]


__all__ = [
    "CaptureHttpDependencies",
    "collect_tencent",
    "collect_push2",
    "collect_sina",
    "collect_sina_extended",
    "collect_baidu",
    "collect_clist",
    "collect_slist",
    "collect_exchange",
    "collect_em_kline_f61",
    "collect_em_fund_flow",
    "collect_ulist239",
    "collect_push2ex",
    "collect_em_hot",
    "collect_cls",
]


def collect_tencent(pool: list) -> dict:
    """腾讯 qt.gtimg 单股全字段(保存原始 split 数组 + 索引名说明)。"""
    from stock_common import _quick_request

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        # V17.0 审查: 原三元 9 先于 92 → 北交所 920 误判 sh(昨日采集 920118/920508 空数据实证);
        # 92 北交所必须先行(与 em_secid_prefix 同口径)
        market = (
            "bj"
            if c.startswith(("92", "8", "4", "43", "83", "87"))
            else ("sh" if c.startswith(("6", "9", "5")) else "sz")
        )
        url = f"https://qt.gtimg.cn/q={market}{c}"
        try:
            r = _quick_request(url, timeout=10)
            if r is None:
                out["stocks"][c] = {"__error__": "request failed"}
                continue
            line = r.text.strip()
            if "=" not in line or '"' not in line:
                out["stocks"][c] = {"__error__": f"parse failed: {line[:100]}"}
                continue
            body = line.split('"')[1]
            fields = body.split("~")
            out["stocks"][c] = {
                "url": url,
                "n_fields": len(fields),
                "fields": fields,  # 原始全字段数组,索引对照 docs/verify/tencent_verify.md
            }
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_push2(pool: list, deps: CaptureHttpDependencies) -> dict:
    """东财 push2 stock/get 显式全字段(f1-f250, EM_FULL_FIELDS)。

    V16.4.1 实测: 不指定 fields 时服务端仅返回 58 字段基础子集(缺 f162/f167 等估值字段),
    故此处显式请求全字段, 与主字典登记口径对齐, 采集不遗漏。2026-08-12 实测: push2 半恢复状态——
    连接级风控仍在,首次连接约 50%
    概率 RemoteDisconnected(健康探测单次连接恰好成功)。V16.4.1 防封:
    失败**不再重试**(重试叠加失败连接会触发封禁),失败即记 error。
    V17.3.2 封禁规律对齐: 跨 33 采集日实证 push2 主域受扰率 80%、push2delay 镜像域可用率
    ~93-97%(独立风控面), 故**优先走 push2delay 镜像域**(与运行时 _FFLOW_HOSTS / get_em_batch_quotes
    一致策略), 主域仅作兜底; 两域字段同构(f1-f250)无损失。used_host 记录实际命中域便于排查。
    """
    EM_FULL_FIELDS = deps.em_full_fields
    _request_failure_summary = deps.request_failure_summary
    _request_is_rate_limited = deps.request_is_rate_limited
    em_secid_prefix = deps.em_secid_prefix
    from stock_common import _quick_request
    from stock_common.sc_network import (
        _em_is_banned,
    )  # V17.4.10 修复: _em_is_banned 定义在 sc_network, 未由 stock_common 包 __init__ 重导出

    # V17.3.2 封禁规律对齐: 跨 33 采集日实证 push2 主域受扰率 80%、push2delay 镜像域
    # 可用率 ~93-97%(独立风控面, 主域被封时仍可用)。故**优先 push2delay 镜像域**,
    # 仅当镜像域连续失败(罕见总封禁)才兜底试 push2 主域; 两域字段同构(f1-f250)无损失。
    # V17.3.17 跨进程封禁共享: push2delay 与 push2 为独立 ban key, 本/他进程标记 push2delay
    # 封禁后此处直接跳过镜像域省一次请求, 走 push2 兜底(用户指令: 全走 push2delay, 仅当其
    # 被封再回退其他 push2 源)。
    fields = EM_FULL_FIELDS  # f1-f250 显式全字段(与主字典口径对齐)
    delay_fail_streak = 0
    primary_fail_streak = 0
    delay_circuit_open = False
    primary_circuit_open = False
    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        secid = em_secid_prefix(c) + c  # V17.0 S3: 统一(修复 92 北交所误判 1.)
        r = None
        used_host = ""
        delay_domain = "push2delay.eastmoney.com"
        primary_domain = "push2.eastmoney.com"
        delay_error: Dict[str, Any] = {}
        primary_error: Dict[str, Any] = {}
        delay_banned = delay_circuit_open or _em_is_banned(delay_domain)
        # 首选 push2delay 镜像域(独立风控面, 实测可用率 ~95%); 若已被任一进程跨进程标记封禁则跳过
        if not delay_banned:
            try:
                r = _quick_request(
                    "https://push2delay.eastmoney.com/api/qt/stock/get",
                    params={
                        "secid": secid,
                        "fltt": "2",
                        "invt": "2",
                        "fields": fields,
                        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                    },
                    headers={"Referer": "https://quote.eastmoney.com/"},
                    timeout=10,
                    max_retries=1,
                    error_out=delay_error,
                )
                if r is not None:
                    used_host = "push2delay"
                    delay_fail_streak = 0
                else:
                    delay_fail_streak += 1
                    if _request_is_rate_limited(delay_error) or delay_fail_streak >= 3:
                        delay_circuit_open = True
            except Exception as exc:
                delay_fail_streak += 1
                r = None
                delay_error = {
                    "kind": "request_exception",
                    "domain": delay_domain,
                    "error_type": type(exc).__name__,
                    "message": str(exc).split("?", 1)[0][:160],
                }
                if delay_fail_streak >= 3:
                    delay_circuit_open = True
        elif _em_is_banned(delay_domain):
            delay_error = {"kind": "ip_banned", "domain": delay_domain, "attempts": 0}
        else:
            delay_error = {
                "kind": "suppressed_after_failures",
                "domain": delay_domain,
                "attempts": 0,
            }
        # 只有在未触发封禁/失败熔断的域上才走备用请求; 每个股票、每个域最多一次。
        if r is None:
            primary_banned = primary_circuit_open or _em_is_banned(primary_domain)
            if not primary_banned:
                try:
                    r = _quick_request(
                        "https://push2.eastmoney.com/api/qt/stock/get",
                        params={
                            "secid": secid,
                            "fltt": "2",
                            "invt": "2",
                            "fields": fields,
                            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                        },
                        headers={"Referer": "https://quote.eastmoney.com/"},
                        timeout=10,
                        max_retries=1,
                        error_out=primary_error,
                    )
                    if r is not None:
                        used_host = "push2"
                        primary_fail_streak = 0
                    else:
                        primary_fail_streak += 1
                        if _request_is_rate_limited(primary_error) or primary_fail_streak >= 3:
                            primary_circuit_open = True
                except Exception as exc:
                    primary_fail_streak += 1
                    r = None
                    primary_error = {
                        "kind": "request_exception",
                        "domain": primary_domain,
                        "error_type": type(exc).__name__,
                        "message": str(exc).split("?", 1)[0][:160],
                    }
                    if primary_fail_streak >= 3:
                        primary_circuit_open = True
            else:
                primary_error = {
                    "kind": (
                        "ip_banned"
                        if _em_is_banned(primary_domain)
                        else "suppressed_after_failures"
                    ),
                    "domain": primary_domain,
                    "attempts": 0,
                }
        if r is None:
            out["stocks"][c] = {
                "__error__": (
                    "request failed ("
                    + _request_failure_summary("push2delay", delay_error)
                    + "; "
                    + _request_failure_summary("push2", primary_error)
                    + ")"
                )
            }
            continue
        try:
            payload = r.json() or {}
            data = payload.get("data") or {}
            if not isinstance(data, dict) or not data:
                out["stocks"][c] = {"__error__": f"{used_host} empty payload (no stock/get data)"}
                continue
        except Exception as exc:
            out["stocks"][c] = {"__error__": f"{used_host} response parse failed: {str(exc)[:160]}"}
            continue
        out["stocks"][c] = {"secid": secid, "host": used_host, "n_fields": len(data), "data": data}
    return out


def collect_sina(pool: list) -> dict:
    """新浪行情 hq.sinajs 全字段(需 Referer)。"""
    from stock_common import _quick_request, UA

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        # M13 修复：原来只把 "6" 判沪市，漏 "5"(沪ETF)/"9"(沪B) → 新浪源误判 sz 污染跨源对照。
        # 与 collect_tencent(:97) 同口径：92/8/4/43/83/87→bj，6/9/5→sh，其余→sz。
        pre = (
            "bj"
            if c.startswith(("92", "8", "4", "43", "83", "87"))
            else ("sh" if c.startswith(("6", "9", "5")) else "sz")
        )
        try:
            r = _quick_request(
                f"https://hq.sinajs.cn/list={pre}{c}",
                headers={"Referer": "https://finance.sina.com.cn/", "User-Agent": UA},
                timeout=8,
            )
            if r is None:
                out["stocks"][c] = {"__error__": "request failed"}
                continue
            text = r.text.strip()
            if "=" not in text:
                out["stocks"][c] = {"__error__": f"parse failed: {text[:80]}"}
                continue
            payload = text.split('"')[1] if '"' in text else ""
            fields = payload.split(",")
            out["stocks"][c] = {"n_fields": len(fields), "fields": fields}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_sina_extended(pool: list, deps: CaptureHttpDependencies) -> dict:
    """Capture Sina's three statement endpoints and per-stock money-flow rows.

    Structured statement rows stay attached to report type, period and item title;
    only the latest money-flow row is also lifted to scalar fields for safe matching.
    Option fields remain explicitly paused because the capture pool has no option
    contract identifiers.
    """
    SINA_CAPTURED_FIELD_CODES = deps.sina_captured_field_codes
    SINA_PAUSED_OPTION_FIELDS = deps.sina_paused_option_fields
    SINA_REQUIRED_FLOW_FIELDS = deps.sina_required_flow_fields
    SINA_UNRESOLVED_FIELD_CODES = deps.sina_unresolved_field_codes
    from stock_common import get_sina_financial_report_raw, get_sina_stock_fund_flow_raw

    report_types = ("fzb", "lrb", "llb")
    output: Dict[str, Any] = {
        "stocks": {},
        "__source_meta__": {
            "structured_paths_archived_only": ["financial_reports.*.report_list.*.data[]"],
            "paused_fields": {
                "codes": list(SINA_PAUSED_OPTION_FIELDS),
                "reason": "requires an option-contract universe; stock pool entries are not option contracts",
            },
            "captured_registry_codes": list(SINA_CAPTURED_FIELD_CODES),
            "unresolved_registry_codes": {
                "codes": list(SINA_UNRESOLVED_FIELD_CODES),
                "reason": "no source-specific endpoint path is documented; do not infer aliases",
            },
            "row_identity_keys": ["item_title", "report period", "report_type"],
            "request_policy": "one attempt per endpoint; stop that endpoint family after first failure",
        },
    }
    finance_available = True
    flow_available = True

    for item in pool:
        code = item["code"]
        record: Dict[str, Any] = {"financial_reports": {}}

        if finance_available:
            for index, report_type in enumerate(report_types):
                report = get_sina_financial_report_raw(code, report_type, num_periods=1)
                if report is None:
                    record["financial_reports"][report_type] = {
                        "__error__": "Sina financial report request or response failed"
                    }
                    finance_available = False
                    for pending_type in report_types[index + 1 :]:
                        record["financial_reports"][pending_type] = {
                            "__skipped__": "deferred: Sina financial endpoint stopped after first failure"
                        }
                    break
                record["financial_reports"][report_type] = report
        else:
            record["financial_reports"] = {
                report_type: {
                    "__skipped__": "deferred: Sina financial endpoint stopped after first failure"
                }
                for report_type in report_types
            }

        if flow_available:
            rows = get_sina_stock_fund_flow_raw(code, days=1)
            if rows is None or not rows:
                record["money_flow"] = {
                    "__error__": "Sina per-stock money-flow request returned no rows"
                }
                flow_available = False
            else:
                record["money_flow"] = rows
                latest = max(
                    rows,
                    key=lambda row: str(row.get("opendate", "")) if isinstance(row, dict) else "",
                )
                missing_fields = (
                    set(SINA_REQUIRED_FLOW_FIELDS) - set(latest)
                    if isinstance(latest, dict)
                    else set(SINA_REQUIRED_FLOW_FIELDS)
                )
                if missing_fields:
                    # Preserve evidence, but do not report a successful field capture
                    # when the upstream contract omitted a registered value.
                    record["__error__"] = (
                        "Sina money-flow response missing registered fields: "
                        + ", ".join(sorted(missing_fields))
                    )
                    flow_available = False
                else:
                    for key in SINA_REQUIRED_FLOW_FIELDS:
                        record[key] = latest[key]
        else:
            record["money_flow"] = {
                "__skipped__": "deferred: Sina money-flow endpoint stopped after first failure"
            }

        output["stocks"][code] = record
    return output


def collect_baidu(pool: list, deps: CaptureHttpDependencies, probe: bool = False) -> dict:
    """Keep Baidu pending by default; explicit ``--only baidu`` enables one probe.

    The dead ``getrelatedblock`` concept endpoint is unrelated to this K-line URL.
    This collector makes at most one request per code and opens a local circuit after
    the first request/shape failure, marking remaining codes as deferred.
    """
    BAIDU_PENDING_FIELD_CODES = deps.baidu_pending_field_codes
    _parse_baidu_kline_probe = deps.parse_baidu_kline_probe
    if not probe:
        return {
            "__unwired__": "pending_validation",
            "registry_name": "百度(baidu)",
            "section": "12.8.16 百度股市通（K线带MA）❌→⏸️",
            "pending_field_codes": list(BAIDU_PENDING_FIELD_CODES),
            "reason": (
                "K线端点当前无法在本机验证；默认不请求。显式运行 --only baidu 可限量复核；"
                "getrelatedblock 失效不作为 K 线失效证据"
            ),
        }

    from stock_common import _quick_request, UA

    url = "https://finance.pae.baidu.com/selfselect/getstockquotation"
    headers = {
        "User-Agent": UA,
        "Accept": "application/vnd.finance-web.v1+json",
        "Origin": "https://gushitong.baidu.com",
        "Referer": "https://gushitong.baidu.com/",
    }
    output: Dict[str, Any] = {
        "stocks": {},
        "__source_meta__": {"probe_mode": "explicit_only", "request_count": 0},
    }
    stopped = False
    for item in pool:
        code = item["code"]
        if stopped:
            output["stocks"][code] = {
                "__skipped__": "deferred: Baidu probe stopped after first request or contract failure"
            }
            continue
        params = {
            "all": "1",
            "isIndex": "false",
            "isBk": "false",
            "isBlock": "false",
            "isFutures": "false",
            "isStock": "true",
            "newFormat": "1",
            "group": "quotation_kline_ab",
            "finClientType": "pc",
            "code": code,
            "start_time": "",
            "ktype": "1",
        }
        output["__source_meta__"]["request_count"] += 1
        try:
            response = _quick_request(
                url, params=params, headers=headers, timeout=10, max_retries=1
            )
            record = _parse_baidu_kline_probe(response.json()) if response is not None else None
        except Exception as exc:
            record = None
            output["__source_meta__"]["failure_sample"] = f"{type(exc).__name__}: {exc}"[:200]
        if record is None:
            output["stocks"][code] = {
                "__error__": "Baidu K-line request failed or response contract is incomplete"
            }
            output["__source_meta__"]["stopped_after_code"] = code
            stopped = True
        else:
            output["stocks"][code] = record
    return output


def collect_clist(pool: list, deps: CaptureHttpDependencies) -> dict:
    """东财 clist(板块排名/板块资金流, §12.8.6)——真实 producer(V17.2.13)。

    走 push2delay 镜像域 clist/get(东财板块榜, 与 push2 主域内容一致、延迟 15min 无影响),
    覆盖 行业(m:90 t:2)/概念(t:3)/地域(t:1) 三类, 按 §12.8.6 登记字段全集抓取原始 f 字段
    (排名 + 今日/5日/10日 资金流)。
    A1: 复用 stock_common._quick_request(分域限流); **主域优先 push2delay**(独立风控面,
    规避 push2 主域 IP 级封禁——实测 push2/push2his/83.push2 同风控面常 20h 冷却封禁,
    而 push2delay/push2ex 独立可用); push2delay 失败回退 push2 主域。
    """
    _request_failure_summary = deps.request_failure_summary
    _request_is_rate_limited = deps.request_is_rate_limited
    from stock_common import _quick_request, UA
    from stock_common.sc_network import _em_is_banned

    # §12.8.6 登记字段全集: 排名(f2/f3/f4/f12/f13/f14/f104/f105/f128/f136/f140/f141/f207)
    # + 资金流今日(f62/f184/f66/f72/f78/f84)/5日(f164/f165/f109/f257)/10日(f174/f175/f160)
    FIELDS = (
        "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207,"
        "f62,f184,f66,f72,f78,f84,f164,f165,f109,f257,f174,f175,f160"
    )
    TYPES = [("industry", "m:90+t:2"), ("concept", "m:90+t:3"), ("area", "m:90+t:1")]
    out: Dict[str, Any] = {"records": [], "by_type": {}}
    domain_blocked = {"push2delay.eastmoney.com": False, "push2.eastmoney.com": False}
    domain_failures = {"push2delay.eastmoney.com": 0, "push2.eastmoney.com": 0}
    domain_errors: Dict[str, Dict[str, Any]] = {}
    for label, fs in TYPES:
        # V17.2.13 稳健分页: 以服务端 data.total 为权威总数驱动翻页, 避免「单页未满即误判末页」
        # 导致的概念板(400+ 只)被截断为 100 的问题; 另设 50 页硬上限防异常死循环。
        all_recs = []
        total = None
        pn = 1
        while pn <= 50:
            params = {
                "po": "1",
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "fs": fs,
                "fields": FIELDS,
                "pz": "200",
                "pn": str(pn),
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            }
            hdr = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
            delay_error: Dict[str, Any] = {}
            primary_error: Dict[str, Any] = {}
            try:
                delay_domain = "push2delay.eastmoney.com"
                primary_domain = "push2.eastmoney.com"
                if domain_blocked[delay_domain]:
                    delay_error = dict(domain_errors.get(delay_domain) or {})
                    delay_error.update({"domain": delay_domain, "attempts": 0})
                    delay_error.setdefault("kind", "suppressed_after_failures")
                    r = None
                elif _em_is_banned(delay_domain):
                    delay_error = {"kind": "ip_banned", "domain": delay_domain, "attempts": 0}
                    r = None
                else:
                    r = _quick_request(
                        "https://push2delay.eastmoney.com/api/qt/clist/get",
                        params=params,
                        headers=hdr,
                        timeout=10,
                        max_retries=1,
                        error_out=delay_error,
                    )
                    if r is None:
                        domain_failures[delay_domain] += 1
                        domain_errors[delay_domain] = dict(delay_error)
                        if (
                            _request_is_rate_limited(delay_error)
                            or domain_failures[delay_domain] >= 3
                        ):
                            domain_blocked[delay_domain] = True
                    else:
                        domain_failures[delay_domain] = 0
                if r is None:
                    if domain_blocked[primary_domain]:
                        primary_error = dict(domain_errors.get(primary_domain) or {})
                        primary_error.update({"domain": primary_domain, "attempts": 0})
                        primary_error.setdefault("kind", "suppressed_after_failures")
                    elif _em_is_banned(primary_domain):
                        primary_error = {
                            "kind": "ip_banned",
                            "domain": primary_domain,
                            "attempts": 0,
                        }
                    else:
                        r = _quick_request(
                            "https://push2.eastmoney.com/api/qt/clist/get",
                            params=params,
                            headers=hdr,
                            timeout=10,
                            max_retries=1,
                            error_out=primary_error,
                        )
                        if r is None:
                            domain_failures[primary_domain] += 1
                            domain_errors[primary_domain] = dict(primary_error)
                            if (
                                _request_is_rate_limited(primary_error)
                                or domain_failures[primary_domain] >= 3
                            ):
                                domain_blocked[primary_domain] = True
                        else:
                            domain_failures[primary_domain] = 0
                if r is None:
                    out["by_type"][label] = {
                        "__error__": (
                            "request failed ("
                            + _request_failure_summary("push2delay", delay_error)
                            + "; "
                            + _request_failure_summary("push2", primary_error)
                            + ")"
                        )
                    }
                    break
                d = (r.json() or {}).get("data") or {}
                if total is None:
                    total = d.get("total")
                diff = d.get("diff") or []
                if isinstance(diff, dict):
                    diff = list(diff.values())
                if not diff:
                    break
                for it in diff:
                    rec = dict(it)
                    rec["_board_type"] = label
                    all_recs.append(rec)
                # 终止条件: 已达权威 total / 本页未满(末页) / 硬上限
                if total is not None and len(all_recs) >= total:
                    break
                if len(diff) < 200:
                    break
                pn += 1
            except Exception as e:
                out["by_type"][label] = {"__error__": str(e)[:200]}
                break
        out["records"].extend(all_recs)
        if all_recs:
            out["by_type"][label] = {"n": len(all_recs), "total": total}
        else:
            # 请求成功但 0 条(板块榜恒有数据)→ 空载荷异常(多见于 push2 主域 IP 封禁
            # 返回空成功响应), 显式标错以免 assess_result 误判 ok(公理 A8 禁止静默迁就)。
            # 下列失败分支(line 484/504)已置 __error__ 的, 此处不覆盖。
            _prev = out["by_type"].get(label, {})
            if "__error__" not in _prev:
                out["by_type"][label] = {
                    "n": 0,
                    "total": total,
                    "__error__": "empty payload (0 records; possible push2 family IP-ban / endpoint anomaly)",
                }
    return out


def collect_slist(pool: list, deps: CaptureHttpDependencies) -> dict:
    """东财 slist(个股所属板块/概念归属, §12.8.5)——真实 producer(V17.2.13, 联网实测修正)。

    V17.2.13 联网实测订正(关键): slist/get **必须带 secid(个股 secid)**, 裸 spt=3(无 secid)
    服务端恒返回 rc:102(拒收)。带 secid 时返回**该股票所属的全部板块**(行业/概念/地域混合一表),
    字段: f12=板块 BK 代码、f14=板块名、f3=板块当日涨跌幅%、f128=板块龙头股名、f140=龙头股代码。
    → 与 §12.8.5「个股所属板块/概念归属」语义完全吻合(逐股返回其归属板块列表)。
    此前字典 §12.8.5 误记为「裸 spt=3 返回全局混合板块列表」, 经本次实测更正(裸 spt=3 → rc:102)。
    A1: 复用 _quick_request(分域限流); **主域优先 push2delay**(独立风控面, 规避 push2 主域 IP 封禁), 失败回退 push2 主域; 周六休市不影响(东财 7×24 快照)。
    逐股请求(20 股), 单股失败记 __error__ 不中断(A8 禁止静默迁就)。
    """
    _request_failure_summary = deps.request_failure_summary
    _request_is_rate_limited = deps.request_is_rate_limited
    em_secid_prefix = deps.em_secid_prefix
    from stock_common import _quick_request, UA
    from stock_common.sc_network import _em_is_banned

    FIELDS = "f12,f14,f3,f128,f140"  # 板块代码/名/涨跌幅/龙头名/龙头代码
    out: Dict[str, Any] = {"stocks": {}}
    domain_blocked = {"push2delay.eastmoney.com": False, "push2.eastmoney.com": False}
    domain_failures = {"push2delay.eastmoney.com": 0, "push2.eastmoney.com": 0}
    domain_errors: Dict[str, Dict[str, Any]] = {}
    for p in pool:
        c = p["code"]
        secid = em_secid_prefix(c) + c
        params = {
            "spt": "3",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "secid": secid,
            "fields": FIELDS,
            "pz": "200",
            "pn": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        }
        hdr = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
        delay_error: Dict[str, Any] = {}
        primary_error: Dict[str, Any] = {}
        try:
            delay_domain = "push2delay.eastmoney.com"
            primary_domain = "push2.eastmoney.com"
            if domain_blocked[delay_domain]:
                delay_error = dict(domain_errors.get(delay_domain) or {})
                delay_error.update({"domain": delay_domain, "attempts": 0})
                delay_error.setdefault("kind", "suppressed_after_failures")
                r = None
            elif _em_is_banned(delay_domain):
                delay_error = {"kind": "ip_banned", "domain": delay_domain, "attempts": 0}
                r = None
            else:
                r = _quick_request(
                    "https://push2delay.eastmoney.com/api/qt/slist/get",
                    params=params,
                    headers=hdr,
                    timeout=10,
                    max_retries=1,
                    error_out=delay_error,
                )
                if r is None:
                    domain_failures[delay_domain] += 1
                    domain_errors[delay_domain] = dict(delay_error)
                    if _request_is_rate_limited(delay_error) or domain_failures[delay_domain] >= 3:
                        domain_blocked[delay_domain] = True
                else:
                    domain_failures[delay_domain] = 0
            if r is None:
                if domain_blocked[primary_domain]:
                    primary_error = dict(domain_errors.get(primary_domain) or {})
                    primary_error.update({"domain": primary_domain, "attempts": 0})
                    primary_error.setdefault("kind", "suppressed_after_failures")
                elif _em_is_banned(primary_domain):
                    primary_error = {"kind": "ip_banned", "domain": primary_domain, "attempts": 0}
                else:
                    r = _quick_request(
                        "https://push2.eastmoney.com/api/qt/slist/get",
                        params=params,
                        headers=hdr,
                        timeout=10,
                        max_retries=1,
                        error_out=primary_error,
                    )
                    if r is None:
                        domain_failures[primary_domain] += 1
                        domain_errors[primary_domain] = dict(primary_error)
                        if (
                            _request_is_rate_limited(primary_error)
                            or domain_failures[primary_domain] >= 3
                        ):
                            domain_blocked[primary_domain] = True
                    else:
                        domain_failures[primary_domain] = 0
            if r is None:
                out["stocks"][c] = {
                    "__error__": (
                        "request failed ("
                        + _request_failure_summary("push2delay", delay_error)
                        + "; "
                        + _request_failure_summary("push2", primary_error)
                        + ")"
                    )
                }
                continue
            d = (r.json() or {}).get("data") or {}
            diff = d.get("diff") or []
            if isinstance(diff, dict):
                diff = list(diff.values())
            if diff:
                out["stocks"][c] = {"secid": secid, "n_boards": len(diff), "boards": diff}
            else:
                # 请求成功但 0 板块(个股恒有归属板块)→ 空载荷异常, 显式标错以免 assess_result
                # 误判 ok(公理 A8 禁止静默迁就)。
                out["stocks"][c] = {
                    "secid": secid,
                    "n_boards": 0,
                    "__error__": "empty payload (0 boards; possible push2 family IP-ban / endpoint anomaly)",
                }
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_exchange(pool: list, deps: CaptureHttpDependencies) -> dict:
    """沪深交易所官方(§12.8.17)——真实 producer(V17.2.14)。

    直连交易所官方龙虎榜端点(深交所 szse.cn + 上交所 query.sse.com.cn),
    抓取 §12.8.17 登记字段 zqdm/zqjc/cjje/plyy(+原始 cjsl/dqrq/bz) 与 sse_raw(沪市全文),
    验证 registry「沪深交易所」源字段。复用 dragon_tiger_backup(_eastmoney.py:1155)
    已验证端点的节流范式: ProxyHandler({}) 直连 + _gen_wait_process_interval 全局节流(A1)。
    注: 龙虎榜仅交易日产出; 非交易日(如周六休市)自动回退到最近交易日快照
    (_last_completed_trading_day 取周五, 交易所历史龙虎榜数据可查, 不受周末影响)。
    """
    _last_completed_trading_day = deps.last_completed_trading_day
    import urllib.request, json, ssl
    from stock_common import UA

    from stock_common.sc_network import _gen_wait_process_interval

    trade_date = _last_completed_trading_day().strftime("%Y-%m-%d")
    out: Dict[str, Any] = {
        "records": [],
        "sse_raw": "",
        "szse_keys": [],
        "n_szse": 0,
        "trade_date": trade_date,
    }
    _ctx = ssl._create_unverified_context()

    # 深交所龙虎榜(结构化 JSON: zqdm/zqjc/cjje/plyy/cjsl/dqrq/bz)
    su = (
        "https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON"
        f"&CATALOGID=1842_xxpl&TABKEY=tab1&txtStart={trade_date}"
        f"&txtEnd={trade_date}&random=0.9"
    )
    try:
        _gen_wait_process_interval()
        req = urllib.request.Request(
            su,
            headers={
                "User-Agent": UA,
                "Referer": "https://www.szse.cn/disclosure/supervision/dealinfo/index.html",
            },
        )
        op = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPSHandler(context=_ctx),
        )
        with op.open(req, timeout=15) as r:
            d = json.loads(r.read())
        if isinstance(d, list) and d:
            rows = d[0].get("data", []) or []
            out["n_szse"] = len(rows)
            if rows:
                out["szse_keys"] = sorted(rows[0].keys())
                out["records"] = rows
    except Exception as e:
        out["__error_szse__"] = str(e)[:200]

    # 上交所龙虎榜(JSONP 全文, 含营业部席位 → sse_raw)
    eu = (
        "https://query.sse.com.cn/infodisplay/showTradePublicFile.do?"
        f"jsonCallBack=cb&isPagination=false&dateTx={trade_date}"
    )
    try:
        _gen_wait_process_interval()
        req = urllib.request.Request(
            eu,
            headers={
                "User-Agent": UA,
                "Referer": "https://www.sse.com.cn/disclosure/diclosure/public/",
            },
        )
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with op.open(req, timeout=15) as r:
            t = r.read().decode("utf-8", "ignore")
        if "(" in t and ")" in t:
            d2 = json.loads(t[t.index("(") + 1 : t.rindex(")")])
            fc = d2.get("fileContents", []) or []
            out["sse_raw"] = "\n".join(fc)
    except Exception as e:
        out["__error_sse__"] = str(e)[:200]

    return out


def collect_em_kline_f61(pool: list, deps: CaptureHttpDependencies) -> dict:
    """东财日K线(**push2his** 域)——f61 换手率为 CYQ 筹码分布唯一源(字典 V17.0.14)。

    TDX 0x0010 日K 与腾讯 ifzq 均无换手率 → 仅东财日K有。
    🔴 域选择实测(2026-09-01 及 2026-09-14 换 IP 后复测三股 600519/000568/601288 均证):
    push2/push2delay 主域 kline **dktotal 恒为 0 空返回**(延时镜像无历史窗口), 故镜像
    **不可补数据且探测它纯耗限流额度、易触发远端重封**——本采集器**仅打 push2his**。
    仅 push2his 有全窗口(dktotal=6004/7736/3924, 150 根)——与生产 `get_cyq_distribution`
    的 `_em_fflow_request(prefer_his=True)` 同源。
    klines 结构: "date,open,close,high,low,volume,amount,amplitude,pct,chg,turnover"
    其中 turnover=f61 换手率; fqt=0 不复权(成本分布口径)。
    V17.2.x 可用性修复: 旧逻辑"连续3败即整段熔断"把后续股票直接判死(从未真试)→ 实测
    13/20 误杀。改为: 每只股票**始终真试 push2his**(限流 0.25rps/4s 由 _quick_request 内置, 2026-09-14 由 0.4rps 进一步放缓以避远端封禁),
    失败仅记 error、不杀域; **仅 dktotal>0 才收**, 杜绝空数据误存。远端 IP 级封禁冷却后
    本采集器不再自伤、自动恢复(东财 push2 族风控面极敏感, 需采集间留足冷却)。
    """
    _em_capture_pause_reason = deps.em_capture_pause_reason
    _request_failure_summary = deps.request_failure_summary
    em_secid_prefix = deps.em_secid_prefix
    from stock_common import _quick_request

    KLINE_FIELDS2 = "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
    out: Dict[str, Any] = {"stocks": {}}
    pause_reason: Optional[str] = None
    consecutive_disconnects = 0
    for p in pool:
        c = p["code"]
        if pause_reason:
            out["stocks"][c] = {"__skipped__": f"source paused after {pause_reason}"}
            continue
        secid = em_secid_prefix(c) + c
        request_error: Dict[str, Any] = {}
        try:
            r = _quick_request(
                "https://push2his.eastmoney.com/api/qt/stock/kline/get",
                params={
                    "secid": secid,
                    "fields1": "f1,f2,f3,f4,f5,f6",
                    "fields2": KLINE_FIELDS2,
                    "klt": "101",
                    "fqt": "0",
                    "end": "20500101",
                    "lmt": "150",
                    "ut": "b2884a393a59ad64002292a3e90d46a5",
                },
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=15,
                max_retries=1,
                error_out=request_error,
            )
        except Exception as exc:
            r = None
            request_error = {
                "kind": "request_exception",
                "domain": "push2his.eastmoney.com",
                "error_type": type(exc).__name__,
                "message": str(exc).split("?", 1)[0][:160],
            }
        if r is None:
            out["stocks"][c] = {"__error__": _request_failure_summary("push2his", request_error)}
            _kind = str(request_error.get("kind") or "").lower()
            consecutive_disconnects = (
                consecutive_disconnects + 1 if _kind in {"connection_error", "timeout"} else 0
            )
            pause_reason = _em_capture_pause_reason(
                "push2his", request_error, consecutive_disconnects
            )
            continue
        consecutive_disconnects = 0
        try:
            payload = r.json() or {}
            data = payload.get("data") or {}
            if not isinstance(data, dict):
                raise ValueError("response data is not an object")
            klines = data.get("klines") or []
            dktotal = data.get("dktotal") or 0
        except Exception as exc:
            out["stocks"][c] = {"__error__": f"push2his response parse failed: {str(exc)[:160]}"}
            continue
        if dktotal and len(klines) > 0:  # 仅真实窗口才算成功, 杜绝空数据误存
            out["stocks"][c] = {
                "secid": secid,
                "dktotal": dktotal,
                "n_klines": len(klines),
                "klines_tail30": klines[-30:],
                "klines_all": klines[:150],
                "host": "push2his",
            }
        else:
            out["stocks"][c] = {"__error__": "push2his empty (dktotal=0)"}
    return out


def collect_em_fund_flow(pool: list, deps: CaptureHttpDependencies) -> dict:
    """东财资金流四档(push2delay 域)——f137 主力净额唯一同口径源(V17.0.16)。

    stock/get: f135/136/137=主力(超大+大单)、f138/139/140=超大单、f141/142/143=大单、
    f144/145/146=中单、f149=小单净。铁证 f137=f140+f143(169/169); ulist f62==f137(96.6%)。
    全走 push2delay 镜像域(独立风控 1.0rps), 不碰 push2 主域。
    """
    _em_capture_pause_reason = deps.em_capture_pause_reason
    _request_failure_summary = deps.request_failure_summary
    em_secid_prefix = deps.em_secid_prefix
    from stock_common import _quick_request

    # V17.1.x: 补全 f147/f148(散单买/卖额, 主字典 §12.3.4 已登记)——原列表漏此二项致采集缺失。
    ff_fields = ",".join(
        [
            "f135",
            "f136",
            "f137",
            "f138",
            "f139",
            "f140",
            "f141",
            "f142",
            "f143",
            "f144",
            "f145",
            "f146",
            "f147",
            "f148",  # 散单(第五档)买/卖额
            "f149",
        ]
    )
    out: Dict[str, Any] = {"stocks": {}}
    pause_reason: Optional[str] = None
    consecutive_disconnects = 0
    for p in pool:
        c = p["code"]
        if pause_reason:
            out["stocks"][c] = {"__skipped__": f"source paused after {pause_reason}"}
            continue
        secid = em_secid_prefix(c) + c
        request_error: Dict[str, Any] = {}
        try:
            r = _quick_request(
                "https://push2delay.eastmoney.com/api/qt/stock/get",
                params={
                    "secid": secid,
                    "fltt": "2",
                    "invt": "2",
                    "fields": ff_fields,
                    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                },
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=10,
                max_retries=1,
                error_out=request_error,
            )
            if r is None:
                out["stocks"][c] = {
                    "__error__": _request_failure_summary("push2delay", request_error)
                }
                _kind = str(request_error.get("kind") or "").lower()
                consecutive_disconnects = (
                    consecutive_disconnects + 1 if _kind in {"connection_error", "timeout"} else 0
                )
                pause_reason = _em_capture_pause_reason(
                    "push2delay", request_error, consecutive_disconnects
                )
                continue
            consecutive_disconnects = 0
            payload = r.json() or {}
            data = payload.get("data") or {}
            if not isinstance(data, dict) or not data:
                out["stocks"][c] = {"__error__": "push2delay empty payload (no stock/get data)"}
                continue
            out["stocks"][c] = {"secid": secid, "n_fields": len(data), "data": data}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_ulist239(pool: list, deps: CaptureHttpDependencies) -> dict:
    """东财 push2delay ulist.np 批量全字段(1 次请求 20 只,字典 §12.9 ulist 239 字段)。"""
    EM_FULL_FIELDS = deps.em_full_fields
    _request_failure_summary = deps.request_failure_summary
    from stock_common import _quick_request

    def _mkt(c):
        if c.startswith(("92", "8", "4", "43", "83", "87")):
            return "0."  # 北交所(920 等)必须先判——"9" 前缀会被沪市分支吃掉(V16.4.1 bug 修复)
        if c.startswith(("6", "5", "9")):
            return "1."
        return "0."

    secids = ",".join(_mkt(p["code"]) + p["code"] for p in pool)
    request_error: Dict[str, Any] = {}
    try:
        r = _quick_request(
            "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
            params={"fltt": "2", "invt": "2", "secids": secids, "fields": EM_FULL_FIELDS},
            headers={"Referer": "https://quote.eastmoney.com/"},
            timeout=15,
            max_retries=1,
            error_out=request_error,
        )
        if r is None:
            return {
                "stocks": {},
                "__error__": _request_failure_summary("push2delay", request_error),
            }
        payload = r.json() or {}
        response_data = payload.get("data") or {}
        diff = response_data.get("diff") or []
        if isinstance(diff, dict):
            diff = list(diff.values())
        out: Dict[str, Any] = {"stocks": {}}
        for item in diff:
            code = str(item.get("f12", ""))
            if code:
                out["stocks"][code] = {"n_fields": len(item), "data": item}
        if not out["stocks"]:
            return {
                "stocks": {},
                "__error__": "push2delay ulist empty payload (0 stock records)",
            }
        for item in pool:
            code = str(item.get("code", ""))
            if code and code not in out["stocks"]:
                out["stocks"][code] = {"__error__": "requested code missing from ulist response"}
        return out
    except Exception as e:
        return {"__error__": str(e)[:200]}


def collect_push2ex(pool: list) -> dict:
    """push2ex 涨停/跌停/炸板池(市场级,字典 §12.9.2)。"""
    out: Dict[str, Any] = {}
    try:
        from stock_common import get_limit_up_pool, get_limit_down_pool, get_limit_broken_pool

        out["limit_up_pool"] = get_limit_up_pool()
        out["limit_down_pool"] = get_limit_down_pool()
        out["limit_broken_pool"] = get_limit_broken_pool()
    except Exception as e:
        out["error"] = str(e)[:200]
    return out


def collect_em_hot(pool: list) -> dict:
    """东财人气榜(市场级,emappdata 域)。"""
    try:
        from stock_common import em_hot_rank

        return {"hot_rank": em_hot_rank(top=50)}
    except Exception as e:
        return {"error": str(e)[:200]}


def collect_cls(pool: list) -> dict:
    """财联社快讯(市场级)。"""
    try:
        from stock_common import cls_telegraph

        return {"telegraph": cls_telegraph(page_size=50)}
    except Exception as e:
        return {"error": str(e)[:200]}
