# -*- coding: utf-8 -*-
"""tests/test_eastmoney_health.py — 东财接口按域名健康度矩阵

背景（2026-08-04 实跑核查）：
  东财不同域名/接口的封禁条件不同（V16.2.5 实测）：
    - datacenter-web（两融/北向/大宗/解禁）：稳定可用
    - push2 / push2his / 83.push2（实时行情/历史资金流）：连接级风控
      （RemoteDisconnected 直接断连，非 403/429，**实测恢复 20+ 小时**（参考仓库 PR#36），
      自动降级走 push2delay/腾讯）
    - push2delay（延时镜像）：可用但仅当日窗口
  本脚本按域名逐一探测，输出每个域的健康状态矩阵，
  快速定位"哪个域被封/恢复正常"，避免报告里接口失败误判为代码 bug。

判定规则（不把接口抖动误报为代码回归）：
  - HTTP 200 + 数据非空          → PASS
  - HTTP 403 / 429               → SKIP（IP 级风控，可恢复）
  - RemoteDisconnected / 连接断开 → SKIP（连接级风控，可恢复）
  - 超时                         → SKIP（网络抖动）
  - 其他异常 / 数据为空           → FAIL（可能为代码/协议问题）

运行方式（需 REAL_NETWORK=1，遵守限流：域间 ≥1.8s 间隔；连续两次运行间隔 ≥5 分钟——
  push2 系阈值极低，0.4rps 连续探测仍可能触发连接级风控，SKIP 属正常现象）：
  $env:REAL_NETWORK=1; .\\scripts\\run_tests.ps1 -Mode module -Path tests/test_eastmoney_health.py -ExtraArgs '-v'  # noqa: W605
"""
from __future__ import annotations

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytestmark = pytest.mark.real_network  # 需 REAL_NETWORK=1 才运行（conftest 拦截）

_PROXIES = {"http": None, "https": None}
_BASE_HDRS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
}
_UT = "f057cbcbce2a86e2866ab8877db1d059"

# 域间最小间隔（限流纪律：东财系密集请求触发 RemoteDisconnected）
_DOMAIN_INTERVAL = 1.8
_last_request_ts = [0.0]


def _check_basic(r, data_key=None, min_rows=1):
    """通用数据校验：data_key 存在且非空 / 至少 min_rows 行（支持 result.data 结构）。"""
    d = r.json() if hasattr(r, "json") else {}
    if data_key is None:
        return bool(d)
    if data_key == "result.data":
        v = ((d.get("result") or {}).get("data")) if isinstance(d.get("result"), dict) else None
    else:
        v = (d.get("data") or {}).get(data_key) if isinstance(d.get("data"), dict) else d.get(data_key)
    if isinstance(v, list):
        return len(v) >= min_rows
    if isinstance(v, dict):
        return bool(v)
    return bool(v)


def _check_klines(r, min_rows=1):
    """fflow daykline：klines 数组非空。"""
    d = r.json() if hasattr(r, "json") else {}
    klines = ((d.get("data") or {}).get("klines")) if isinstance(d.get("data"), dict) else []
    return isinstance(klines, list) and len(klines) >= min_rows


def _check_rc(r):
    """东财 rc 语义：0=成功（data 非空）；205=接口正常但当日无数据（如涨停池休市日）；
    100=无数据（push2delay 早盘当日 klines 未生成时返回）。"""
    d = r.json() if hasattr(r, "json") else {}
    rc = d.get("rc")
    if rc == 0:
        return d.get("data") is not None
    return rc in (100, 205)


def _check_post_json(r):
    """emappdata POST JSON：data 数组非空。"""
    d = r.json() if hasattr(r, "json") else {}
    return isinstance(d.get("data"), list) and len(d["data"]) > 0


# ── 域名矩阵：每个域一个代表接口（贴近项目实际使用路径）────────────
EASTMONEY_DOMAINS = [
    # (域名, 测试名, url, params, check, 说明, method)
    (
        "push2",
        "push2 ulist 行业/概念(f100/f103)",
        "https://push2.eastmoney.com/api/qt/ulist.np/get",
        {"fltt": "2", "invt": "2", "secids": "1.600519",
         "fields": "f12,f14,f100,f102,f103,f112,f113", "ut": _UT},
        lambda r: _check_basic(r, "diff", 1),
        "实时行情/行业概念主域（V16.2.5 曾连接级风控）",
        "GET",
    ),
    (
        "push2his",
        "push2his fflow daykline 历史资金流",
        "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get",
        {"lmt": "5", "klt": "101", "secid": "0.000100",
         "fields1": "f1,f2,f3,f7", "fields2": "f51,f52,f53,f54,f55,f56", "ut": _UT},
        _check_klines,
        "历史资金流主域（全窗口；V16.2.5 曾连接级风控）",
        "GET",
    ),
    (
        "push2delay",
        "push2delay fflow daykline 延时镜像",
        "https://push2delay.eastmoney.com/api/qt/stock/fflow/daykline/get",
        {"lmt": "5", "klt": "101", "secid": "0.000100",
         "fields1": "f1,f2,f3,f7", "fields2": "f51,f52,f53,f54,f55,f56", "ut": _UT},
        _check_rc,
        "延时 15 分钟镜像（仅当日；早盘 rc=100 无当日数据正常）",
        "GET",
    ),
    (
        "push2ex",
        "push2ex 昨日涨停池",
        "https://push2ex.eastmoney.com/getTopicZTPool",
        {"ut": _UT, "dpt": "wz.ztzt", "Pageindex": "0", "pagesize": "5",
         "sort": "fbt:asc", "date": "20260803"},
        _check_rc,
        "涨停/炸板/跌停池域（与 push2 共用风控面；rc=205=当日无数据正常）",
        "GET",
    ),
    (
        "83.push2",
        "83.push2 clist 全市场排行",
        "http://83.push2.eastmoney.com/api/qt/clist/get",
        {"pn": "1", "pz": "2", "po": "1", "np": "1", "fltt": "2", "invt": "2",
         "fs": "m:0 t:6,m:0 t:80", "fields": "f12,f14,f2,f3", "ut": _UT},
        lambda r: _check_basic(r, "diff", 1),
        "行情列表负载均衡域",
        "GET",
    ),
    (
        "datacenter-web",
        "datacenter-web RPT_LIFT_STAGE 解禁",
        "https://datacenter-web.eastmoney.com/api/data/v1/get",
        {"reportName": "RPT_LIFT_STAGE", "columns": "ALL",
         "filter": '(SECURITY_CODE="000100")', "pageNumber": "1", "pageSize": "2",
         "sortColumns": "FREE_DATE", "sortTypes": "-1",
         "source": "WEB", "client": "WEB"},
        lambda r: _check_basic(r, "result.data", 1),
        "解禁/两融/北向/大宗权威域（实测稳定）",
        "GET",
    ),
    (
        "datacenter",
        "datacenter 通用数据中心",
        "https://datacenter.eastmoney.com/api/data/v1/get",
        {"reportName": "RPT_DAILYBILLBOARD_DETAILSNEW", "columns": "ALL",
         "pageNumber": "1", "pageSize": "1", "sortColumns": "TRADE_DATE", "sortTypes": "-1"},
        lambda r: _check_basic(r, "result.data", 1),
        "数据中心备胎域",
        "GET",
    ),
    (
        "reportapi",
        "reportapi 研报列表",
        "https://reportapi.eastmoney.com/report/list",
        {"pageSize": "1", "industry": "*", "rating": "*",
         "beginTime": "2024-01-01", "endTime": "2030-01-01", "pageNo": "1",
         "code": "600519", "qType": "0"},
        lambda r: isinstance(r.json(), dict) and r.json().get("data") is not None,
        "研报接口域",
        "GET",
    ),
    (
        "np-weblist",
        "np-weblist 7×24 快讯(getFastNewsList)",
        "https://np-weblist.eastmoney.com/comm/web/getFastNewsList",
        {"client": "web", "biz": "web_724", "fastColumn": "102",
         "sortEnd": "", "pageSize": "2", "req_trace": "health-check"},
        lambda r: _check_basic(r, "fastNewsList", 1),
        "快讯接口域（项目 get_eastmoney_global_news 实际路径）",
        "GET",
    ),
    (
        "emappdata",
        "emappdata 人气热榜(POST JSON)",
        "https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
        None,
        _check_post_json,
        "热榜接口域（POST + JSON body；项目 em_hot_concept 实际路径）",
        "POST",
    ),
    (
        "mobappconfig",
        "mobappconfig 重点监控池",
        "https://mobappconfig.securities.eastmoney.com/emcfg/stock_monitor.json",
        None,
        lambda r: isinstance(r.json(), list) and len(r.json()) > 0,
        "配置/监控池域（无 push2 风控面）",
        "GET",
    ),
    (
        "search-api-web",
        "search-api-web 搜索联想",
        "https://search-api-web.eastmoney.com/search/jsonp",
        {"cb": "cb", "param": '{"uid":"","keyword":"TCL","type":["cmsArticleWebOld"],"client":"web","clientVersion":"curr","param":{"cmsArticleWebOld":{"searchScope":"default","sort":"default","pageIndex":1,"pageSize":1,"preTag":"","postTag":""}}}',
         "_": "1", "ut": _UT},
        lambda r: r.status_code == 200,
        "搜索接口域",
        "GET",
    ),
    (
        "quote",
        "quote 行情页面静态资源",
        "https://quote.eastmoney.com/",
        None,
        lambda r: r.status_code == 200 and "eastmoney" in (r.text or ""),
        "行情页面域（Referer 来源）",
        "GET",
    ),
]


def _request_domain(url, params, method="GET"):
    """域请求 + 域间间隔（遵守限流纪律）。emappdata 走 POST + JSON body。"""
    import json as _json
    import requests

    global _last_request_ts
    elapsed = time.time() - _last_request_ts[0]
    if elapsed < _DOMAIN_INTERVAL:
        time.sleep(_DOMAIN_INTERVAL - elapsed)
    _last_request_ts[0] = time.time()

    headers = dict(_BASE_HDRS)
    if method == "POST":
        headers["Content-Type"] = "application/json"
        return requests.post(url, data=_json.dumps({
            "appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38",
            "marketType": "", "pageNo": 1, "pageSize": 3,
        }), headers=headers, timeout=12, proxies=_PROXIES, verify=True)
    kwargs = {"headers": headers, "timeout": 12, "proxies": _PROXIES, "verify": True}
    if params is not None:
        kwargs["params"] = params
    return requests.get(url, **kwargs)


@pytest.mark.parametrize(
    "domain,title,url,params,check,note,method",
    [(d[0], d[1], d[2], d[3], d[4], d[5], d[6]) for d in EASTMONEY_DOMAINS],
    ids=[d[0] for d in EASTMONEY_DOMAINS],
)
def test_eastmoney_domain_health(domain, title, url, params, check, note, method):
    """按域名探测东财接口健康度：PASS / SKIP(风控可恢复) / FAIL(代码或协议问题)。

    命名含域名 → pytest 输出即为健康度矩阵：
      test_eastmoney_domain_health[push2] ...
      test_eastmoney_domain_health[datacenter-web] ...
    """
    import requests

    last_err = None
    r = None
    for attempt in range(2):  # 抖动重试 1 次
        try:
            r = _request_domain(url, params, method)
            if r.status_code == 200:
                break
            last_err = f"HTTP {r.status_code}"
        except Exception as e:  # noqa: BLE001 — 需捕获所有网络异常做判定
            last_err = f"{type(e).__name__}: {str(e)[:120]}"
        time.sleep(3)
    else:
        # 风控判定：连接级/403/429/超时 → SKIP（可恢复，非代码回归）
        if last_err and any(k in last_err for k in (
            "RemoteDisconnected", "ConnectionError", "Connection aborted",
            "403", "429", "Forbidden", "Timeout", "timed out", "ConnectionReset",
        )):
            pytest.skip(f"[{domain}] {title} — 东财风控/网络抖动（可恢复）: {last_err}")
        pytest.fail(f"[{domain}] {title} — 请求失败: {last_err}")

    # 200 但校验失败 → FAIL（可能协议变化，需要关注）
    try:
        assert check(r), f"[{domain}] {title} — HTTP 200 但数据校验失败（协议可能变更）"
    except AssertionError:
        body = (r.text or "")[:150] if r is not None else ""
        pytest.fail(f"[{domain}] {title} — HTTP 200 但数据校验失败（协议可能变更）: {body}")


import pytest
from stock_common import (
    eastmoney_datacenter,
    get_reports,
    get_eastmoney_stock_news,
    get_holder_structure,
    get_northbound_hold,
    get_margin_trading,
    get_block_trade,
    get_lockup_expiry,
    get_industry_comparison,
    get_industry_peers,
    get_stock_sector_rank,
    get_gross_margin_and_roe,
    em_hot_concept,
    eastmoney_stock_info_push2
)

@pytest.mark.real_network
def test_eastmoney_datacenter():
    data = eastmoney_datacenter("600519", "RPT_DAILYBILLBOARD_DETAILSNEW",
                                columns="SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE",
                                page_size=5, sort_columns="TRADE_DATE", sort_types="-1")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_reports():
    data = get_reports("600519", max_pages=1)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_eastmoney_stock_news():
    data = get_eastmoney_stock_news("600519", page_size=5)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_holder_structure():
    data = get_holder_structure("600519")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_northbound_hold():
    data = get_northbound_hold("600519", days=2)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_margin_trading():
    data = get_margin_trading("600519")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_block_trade():
    data = get_block_trade("600519")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_lockup_expiry():
    data = get_lockup_expiry("600519", days=90)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_industry_comparison():
    data = get_industry_comparison(top_n=2)
    assert isinstance(data, dict)

@pytest.mark.real_network
def test_get_industry_peers():
    data = get_industry_peers("600519", top_n=2)
    assert isinstance(data, dict)

@pytest.mark.real_network
def test_get_stock_sector_rank():
    data = get_stock_sector_rank("600519")
    assert data is None or isinstance(data, dict)

@pytest.mark.real_network
def test_get_gross_margin_and_roe():
    data = get_gross_margin_and_roe("600519")
    assert data is None or isinstance(data, dict)

@pytest.mark.real_network
def test_em_hot_concept():
    data = em_hot_concept("600519")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_eastmoney_push2():
    data = eastmoney_stock_info_push2("600519")
    assert isinstance(data, dict)
