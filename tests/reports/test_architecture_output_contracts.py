"""Actual offline generator smoke contracts for all five Markdown reports."""

from __future__ import annotations

import asyncio
import inspect
import ipaddress
import socket
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import mock

import pandas as pd
import pytest

import get_lng_report as lng_report
import get_mak_report as mak_report
import get_med_report as med_report
import get_sht_report as sht_report
import get_val_report as val_report
import stock_common
import stock_common.sc_datasource as sc_datasource
import stock_common.sc_market_signals as sc_market_signals
from core import data_provider, eltdx_adapter, tdx_client, zhb_client


class _ReportCData:
    """Small canonical-data fixture with safe defaults for report-only branches."""

    def __init__(self) -> None:
        self.code = "600000"
        self.name = "测试股"
        self.industry = "测试行业"
        self.board = "主板"
        self.price = 10.0
        self.change_pct = 0.0
        self.open = 10.0
        self.prev_close = 10.0
        self.high = 10.0
        self.low = 10.0
        self.high_52w = 12.0
        self.low_52w = 8.0
        self.high_52w_date = "2026-10-20"
        self.low_52w_date = "2026-01-05"
        self.quote_date = "2026-10-20"
        self.time_anchor = "t-1"
        self.collected_at = "2026-10-21T08:00:00+08:00"
        self.field_sources: dict[str, str] = {}
        self.field_as_of_dates: dict[str, str] = {}
        self.total_shares_wan = 100_000.0
        self.float_shares_wan = 80_000.0
        self.amount_wan = 0.0
        self.turnover_pct = 0.0
        self.limit_up = 11.0
        self.limit_down = 9.0
        self.mcap_yi = 100.0
        self.float_mcap_yi = 80.0
        self.pe_ttm = 15.0
        self.pe_dynamic = 15.0
        self.pe_lyr = 16.0
        self.pb = 1.5
        self.dividend_yield = 1.0
        self.change_5d = 0.0
        self.change_10d = 0.0
        self.change_20d = 0.0
        self.change_60d = 0.0
        self.change_ytd = 0.0
        self.change_mtd = 0.0
        self.is_st = False
        self.is_new = False
        self.list_date = "2000-01-01"
        self.listing_days = 9000
        self.sec_type = 1
        self.eltdx_has_shortline = False
        self.eltdx_ladder_level = 0
        self.eltdx_seal_to_float_ratio = 0.0
        self.eltdx_open_volume_ratio = 0.0
        self.eltdx_limit_board_text = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "industry": self.industry,
            "price": self.price,
            "change_pct": self.change_pct,
            "quote_date": self.quote_date,
            "time_anchor": self.time_anchor,
            "pe_ttm": self.pe_ttm,
            "pb": self.pb,
        }

    def __getattr__(self, name: str) -> Any:
        if name.endswith(("_date", "_source", "_text")):
            return ""
        if name.endswith(("_sources", "_as_of_dates")):
            return {}
        return 0


class _ImmediateAwaitable:
    def __init__(self, value: Any) -> None:
        self.value = value

    def __await__(self):
        if False:
            yield None
        return self.value


def _complete_without_event_loop(awaitable: Any) -> Any:
    iterator = awaitable.__await__()
    try:
        next(iterator)
    except StopIteration as completed:
        return completed.value
    iterator.close()
    raise AssertionError("report coroutine suspended on an unmocked awaitable")


def _default_for(name: str) -> Any:
    if name == "get_canonical_stock_data":
        return _ReportCData()
    if name == "get_stock_info":
        return {"name": "测试股", "industry": "测试行业", "list_date": "2000-01-01"}
    if name == "get_market_status":
        return "closed", "offline test"
    if name == "get_market_snapshot_async":
        return {
            "600000": {
                "code": "600000",
                "name": "测试股",
                "price": 10.0,
                "change_pct": 0.0,
                "volume": 0.0,
                "amount": 0.0,
            }
        }
    if name == "get_market_abnormal_data":
        return []
    if name == "get_concept_blocks":
        return {"industry": [], "concept": []}
    if name == "get_industry_peers":
        return {"peers": []}
    if name == "get_index_returns":
        return {}, {}
    if name.startswith("get_fund_flow"):
        return {"data": [], "error": ""}
    if name == "get_zhb_data_date":
        return "2026-10-20"
    if name == "get_zhb":
        return SimpleNamespace(unified_name_map={})
    if name in {"get_zhb_streak_days", "get_kpl_broken_ratio", "get_kpl_up_down"}:
        return 0
    if name in {"get_eps_forecast_async", "get_eps_forecast"}:
        return pd.DataFrame()
    if name.startswith("is_"):
        return False
    list_markers = (
        "announcement",
        "block_trade",
        "dragon_tiger",
        "holder",
        "history",
        "lockup",
        "margin_trading",
        "northbound",
        "news",
        "reports",
        "strategic",
        "hot_pool",
        "concepts",
        "market_abnormal",
        "limit_pool",
        "sector_stocks",
        "research_section",
        "einteraction_section",
        "event_driven_section",
        "market_signals_section",
    )
    if any(marker in name for marker in list_markers):
        return []
    return {}


def _is_source_callable(name: str, value: Any) -> bool:
    if not callable(value) or name == "render_md_report":
        return False
    prefixes = (
        "get_",
        "fetch_",
        "holder_",
        "render_",
        "tdx_",
        "em_",
        "is_",
        "industry_comparison",
        "prewarm_canonical_quote_cache",
        "em_hot_rank",
        "ths_hot_reason",
        "strategy_",
    )
    return name.startswith(prefixes)


def _patch_source_calls(monkeypatch: pytest.MonkeyPatch, report_module: Any) -> None:
    modules = (
        report_module,
        stock_common,
        sc_datasource,
        sc_market_signals,
        data_provider,
        eltdx_adapter,
        tdx_client,
        zhb_client,
    )
    seen: set[tuple[int, str]] = set()
    for owner in modules:
        for name, original in vars(owner).items():
            key = (id(owner), name)
            if key in seen or not _is_source_callable(name, original):
                continue
            seen.add(key)
            result = _default_for(name)
            if inspect.iscoroutinefunction(original):
                replacement = mock.AsyncMock(return_value=result)
            else:
                replacement = mock.Mock(return_value=result)
            monkeypatch.setattr(owner, name, replacement)


async def _generate(report_type: str, path: Path) -> Any:
    session = mock.MagicMock()
    if report_type == "sht":
        return await sht_report.generate_report_async(
            session, "600000", str(path), ind_comp={}, idx_q={}, hsgt={}
        )
    if report_type == "med":
        return await med_report.generate_report_async(
            session, "600000", str(path), ind_comp={}, hsgt={}
        )
    if report_type == "lng":
        return await lng_report.generate_report_async(session, "600000", str(path), ind_comp={})
    if report_type == "val":
        return await val_report.run_discovery_async(str(path))
    if report_type == "mak":
        return await mak_report.generate_sector_report(str(path))
    raise AssertionError(f"unexpected report type: {report_type}")


@pytest.mark.parametrize(
    ("report_type", "report_module", "expected_text", "expected_section"),
    [
        (
            "sht",
            sht_report,
            "600000 个股深度数据报告",
            "## 一、个股基本信息",
        ),
        (
            "med",
            med_report,
            "600000 中线深度投研报告",
            "## 二、个股基本信息与估值锚点",
        ),
        (
            "lng",
            lng_report,
            "600000 长线价投专属深度体检报告",
            "## 一、企业基本盘与绝对估值锚点",
        ),
        ("val", val_report, "A 股策略发现报告", "扫描结果汇总:"),
        ("mak", mak_report, "A股异动及行业轮动扫描报告", "## A. 全市场情绪监测看板"),
    ],
)
def test_report_generator_writes_utf8_markdown_offline(
    report_type: str,
    report_module: Any,
    expected_text: str,
    expected_section: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    network_attempts: list[str] = []

    def deny_network(*args: Any, **kwargs: Any) -> None:
        network_attempts.append(repr(args[:2]))
        raise AssertionError("offline report contract attempted a network connection")

    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_getaddrinfo = socket.getaddrinfo

    def is_loopback(host: Any) -> bool:
        if host in {"localhost", "localhost."}:
            return True
        try:
            return ipaddress.ip_address(host).is_loopback
        except (TypeError, ValueError):
            return False

    def guarded_connect(sock: socket.socket, address: Any) -> Any:
        host = address[0] if isinstance(address, tuple) else address
        if is_loopback(host):
            return original_connect(sock, address)
        deny_network(sock, address)

    def guarded_connect_ex(sock: socket.socket, address: Any) -> Any:
        host = address[0] if isinstance(address, tuple) else address
        if is_loopback(host):
            return original_connect_ex(sock, address)
        deny_network(sock, address)

    def guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
        if is_loopback(host):
            return original_getaddrinfo(host, *args, **kwargs)
        deny_network(host, *args)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    _patch_source_calls(monkeypatch, report_module)
    if report_module is sht_report:

        async def empty_datacenter(kind: str, *_args: Any, **_kwargs: Any) -> Any:
            if kind == "dragon_tiger":
                return {"records": [], "institution": {}}
            if kind == "lockup":
                return {"history": [], "upcoming": []}
            return []

        monkeypatch.setattr(
            sc_datasource,
            "resolve_datacenter",
            mock.AsyncMock(side_effect=empty_datacenter),
        )

    def immediate_to_thread(function: Any, /, *args: Any, **kwargs: Any) -> _ImmediateAwaitable:
        if not isinstance(function, mock.Mock):
            raise AssertionError(f"unmocked threaded data function: {function!r}")
        return _ImmediateAwaitable(function(*args, **kwargs))

    def immediate_sleep(*_args: Any, **_kwargs: Any) -> _ImmediateAwaitable:
        return _ImmediateAwaitable(None)

    def immediate_gather(*awaitables: Any, return_exceptions: bool = False) -> _ImmediateAwaitable:
        results = []
        for awaitable in awaitables:
            try:
                results.append(_complete_without_event_loop(awaitable))
            except Exception as exc:
                if not return_exceptions:
                    raise
                results.append(exc)
        return _ImmediateAwaitable(results)

    def immediate_wait_for(awaitable: Any, *_args: Any, **_kwargs: Any) -> _ImmediateAwaitable:
        return _ImmediateAwaitable(_complete_without_event_loop(awaitable))

    monkeypatch.setattr(asyncio, "to_thread", immediate_to_thread)
    monkeypatch.setattr(asyncio, "sleep", immediate_sleep)
    monkeypatch.setattr(asyncio, "gather", immediate_gather)
    monkeypatch.setattr(asyncio, "wait_for", immediate_wait_for)

    output_path = tmp_path / f"{report_type}.md"
    returned = _complete_without_event_loop(_generate(report_type, output_path))

    assert output_path.is_file()
    content = output_path.read_text(encoding="utf-8")
    assert expected_text in content
    assert expected_section in content
    assert "2026-10-20" in content
    assert content.strip()
    assert returned == content
    assert network_attempts == []
