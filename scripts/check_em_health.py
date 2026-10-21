"""低频、只读的东方财富端点诊断。

默认每个代表性端点最多请求一次，使用项目共享限流与封禁状态。结果只记录主机、路径、
状态、响应结构和日期证据，不保存查询参数或响应正文。

用法:
    python scripts/check_em_health.py
    python scripts/check_em_health.py --probe push2his
    python scripts/check_em_health.py --once

退出码: 0=所选探测均有有效结构; 1=实际请求或响应结构失败; 2=被本地保护跳过/无数据，结论不确定。
诊断 JSON 默认写入仓库 .tmp/eastmoney_health/。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional

for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

INTER_PROBE_SECONDS = 5.0
_SUPPRESSED_KINDS = {
    "ip_banned",
    "circuit_open",
    "suppressed_after_failures",
    "blocked_until_manual_review",
}
_TRANSPORT_KINDS = {
    "connection_error",
    "timeout",
    "request_error",
    "request_exception",
}
_FAILURE_STATES = {
    "diagnostic_error",
    "http_error",
    "invalid_payload",
    "rate_limited",
    "request_error",
    "transport_error",
    "unexpected_payload",
}
_INCONCLUSIVE_STATES = {"empty_data", "not_probed", "suppressed"}


@dataclass(frozen=True)
class ProbeSpec:
    name: str
    risk_family: str
    host: str
    path: str
    params: tuple[tuple[str, str], ...]
    contract: str
    requested_data_date: Optional[str] = None


def _latest_data_date() -> date:
    """Use the project trading calendar; this lookup performs no network request."""
    from stock_common.stock_calendar import latest_market_data_date

    return latest_market_data_date()


def _build_probes(data_date: date) -> list[ProbeSpec]:
    day = data_date.strftime("%Y%m%d")
    start = (data_date - timedelta(days=20)).strftime("%Y%m%d")
    return [
        ProbeSpec(
            "push2",
            "push2_family",
            "push2.eastmoney.com",
            "/api/qt/stock/get",
            (("secid", "1.600519"), ("fields", "f43,f57,f58,f167")),
            "stock_get",
        ),
        ProbeSpec(
            "83.push2",
            "push2_family",
            "83.push2.eastmoney.com",
            "/api/qt/clist/get",
            (
                ("pn", "1"),
                ("pz", "5"),
                ("po", "1"),
                ("np", "1"),
                ("fltt", "2"),
                ("invt", "2"),
                ("fid", "f3"),
                ("fs", "m:1+t:2"),
                ("fields", "f12,f14,f2,f3"),
            ),
            "clist",
        ),
        ProbeSpec(
            "push2delay",
            "push2delay_family",
            "push2delay.eastmoney.com",
            "/api/qt/stock/get",
            (("secid", "1.600519"), ("fields", "f43,f57,f58,f167")),
            "stock_get",
        ),
        ProbeSpec(
            "push2his",
            "push2_family",
            "push2his.eastmoney.com",
            "/api/qt/stock/kline/get",
            (
                ("secid", "1.600519"),
                ("fields1", "f1,f2,f3"),
                ("fields2", "f51,f52,f53"),
                ("klt", "101"),
                ("fqt", "1"),
                ("beg", start),
                ("end", day),
            ),
            "kline",
            day,
        ),
        ProbeSpec(
            "push2ex",
            "push2ex_family",
            "push2ex.eastmoney.com",
            "/getTopicZTPool",
            (
                ("ut", "7eea3edcaed734bea9cbfc24409ed989"),
                ("dpt", "wz.ztzt"),
                ("Pageindex", "0"),
                ("pagesize", "1"),
                ("sort", "fbt:asc"),
                ("date", day),
            ),
            "push2ex",
            day,
        ),
        ProbeSpec(
            "datacenter-web",
            "datacenter_family",
            "datacenter-web.eastmoney.com",
            "/api/data/v1/get",
            (
                ("reportName", "RPT_MUTUAL_DEAL_HISTORY"),
                ("columns", "ALL"),
                ("pageNumber", "1"),
                ("pageSize", "1"),
            ),
            "datacenter",
        ),
    ]


def _throttled_get(
    spec: ProbeSpec,
    *,
    timeout: int = 10,
    error_out: Optional[dict[str, Any]] = None,
) -> Any:
    """Send exactly one attempt through the shared limiter; never fall back to裸 requests."""
    from stock_common.sc_network import _quick_request

    return _quick_request(
        f"https://{spec.host}{spec.path}",
        params=dict(spec.params),
        timeout=timeout,
        max_retries=1,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Referer": "https://quote.eastmoney.com/",
        },
        error_out=error_out,
    )


def _shape_summary(payload: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {"root_type": type(payload).__name__}
    if isinstance(payload, dict):
        summary["root_keys"] = sorted(str(key) for key in payload)[:20]
        for key in ("data", "result"):
            value = payload.get(key)
            if isinstance(value, dict):
                section: dict[str, Any] = {
                    "type": "object",
                    "keys": sorted(str(item) for item in value)[:20],
                }
                for child_key, child_value in value.items():
                    if isinstance(child_value, list):
                        section.setdefault("list_lengths", {})[str(child_key)] = len(child_value)
                summary[key] = section
            elif isinstance(value, list):
                summary[key] = {"type": "array", "length": len(value)}
            elif key in payload:
                summary[key] = {"type": type(value).__name__}
    elif isinstance(payload, list):
        summary["length"] = len(payload)
    return summary


def _contract_state(contract: str, payload: Any) -> tuple[str, Optional[str]]:
    if not isinstance(payload, dict):
        return "unexpected_payload", "root is not a JSON object"

    if contract == "stock_get":
        data = payload.get("data")
        if not isinstance(data, dict):
            return "unexpected_payload", "data is not an object"
        return ("ok", None) if data else ("empty_data", "data object is empty")

    if contract == "clist":
        data = payload.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("diff"), list):
            return "unexpected_payload", "data.diff is not an array"
        if not data["diff"]:
            return "empty_data", "data.diff is empty"
        return "ok", None

    if contract == "push2ex":
        if payload.get("rc") == 205:
            return "empty_data", "endpoint rc=205: no records for requested date"
        data = payload.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("pool"), list):
            return "unexpected_payload", "data.pool is not an array"
        return ("ok", None) if data["pool"] else ("empty_data", "data.pool is empty")

    if contract == "kline":
        data = payload.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("klines"), list):
            return "unexpected_payload", "data.klines is not an array"
        return ("ok", None) if data["klines"] else ("empty_data", "data.klines is empty")

    if contract == "datacenter":
        result = payload.get("result")
        if not isinstance(result, dict) or not isinstance(result.get("data"), list):
            return "unexpected_payload", "result.data is not an array"
        return ("ok", None) if result["data"] else ("empty_data", "result.data is empty")

    return "unexpected_payload", "unknown probe contract"


def _response_data_dates(payload: Any) -> list[str]:
    dates: set[str] = set()
    date_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}|\d{8})(?:[, T].*)?$")

    def add(value: Any) -> None:
        if not isinstance(value, str):
            return
        match = date_pattern.match(value.strip())
        if not match:
            return
        candidate = match.group(1)
        if len(candidate) == 8:
            candidate = f"{candidate[:4]}-{candidate[4:6]}-{candidate[6:8]}"
        try:
            date.fromisoformat(candidate)
        except ValueError:
            return
        dates.add(candidate)

    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if isinstance(data, dict):
        klines = data.get("klines")
        if isinstance(klines, list):
            for row in klines[:1] + klines[-1:]:
                add(row.split(",", 1)[0] if isinstance(row, str) else row)
        for list_key in ("diff", "data"):
            rows = data.get(list_key)
            if isinstance(rows, list):
                for row in rows[:1] + rows[-1:]:
                    if isinstance(row, dict):
                        for key in ("date", "TRADE_DATE", "trade_date", "f51"):
                            add(row.get(key))
    result = payload.get("result")
    if isinstance(result, dict) and isinstance(result.get("data"), list):
        rows = result["data"]
        for row in rows[:1] + rows[-1:]:
            if isinstance(row, dict):
                for key in ("TRADE_DATE", "trade_date", "date"):
                    add(row.get(key))
    return sorted(dates)


def _suppressed_before_request(detail: dict[str, Any]) -> bool:
    kind = str(detail.get("kind") or "").lower()
    attempts = detail.get("attempts")
    return kind in _SUPPRESSED_KINDS and (attempts is None or attempts == 0)


def probe(spec: ProbeSpec) -> dict[str, Any]:
    started = time.monotonic()
    error_detail: dict[str, Any] = {}
    base: dict[str, Any] = {
        "name": spec.name,
        "risk_family": spec.risk_family,
        "host": spec.host,
        "path": spec.path,
        "requested_data_date": spec.requested_data_date,
        "source_data_date_basis": (
            "returned_rows"
            if spec.contract == "kline"
            else (
                "explicit_query_date"
                if spec.contract == "push2ex"
                else "not_explicitly_declared_by_endpoint"
            )
        ),
    }
    try:
        response = _throttled_get(spec, error_out=error_detail)
    except Exception as exc:
        return {
            **base,
            "state": "diagnostic_error",
            "stage": "client_setup",
            "client_attempted": False,
            "client_attempts": 0,
            "error_type": type(exc).__name__,
            "stop_family": True,
            "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
        }

    elapsed_ms = round((time.monotonic() - started) * 1000, 1)
    if response is None:
        kind = str(error_detail.get("kind") or "request_error").lower()
        attempts = error_detail.get("attempts", 0)
        try:
            client_attempts = max(0, int(attempts or 0))
        except (TypeError, ValueError):
            client_attempts = 0
        status_code = error_detail.get("status_code")
        if _suppressed_before_request(error_detail):
            state = "suppressed"
            stage = "local_guard"
        elif kind in {"http_403", "http_429", "rate_limited"} or status_code in (403, 429):
            state = "rate_limited"
            stage = "http_response"
        elif kind in _TRANSPORT_KINDS:
            state = "transport_error"
            stage = "transport"
        elif kind == "ip_banned":
            state = "rate_limited"
            stage = "transport_or_ban_detection"
        elif status_code is not None:
            state = "http_error"
            stage = "http_response"
        else:
            state = "request_error"
            stage = "request"
        return {
            **base,
            "state": state,
            "stage": stage,
            "client_attempted": client_attempts > 0,
            "client_attempts": client_attempts,
            "http_status": status_code,
            "failure_kind": kind,
            "error_type": error_detail.get("error_type"),
            "stop_family": state in {"suppressed", "rate_limited", "transport_error"},
            "elapsed_ms": elapsed_ms,
        }

    status_code = int(response.status_code)
    content = getattr(response, "content", b"")
    if isinstance(content, str):
        response_bytes = len(content.encode("utf-8", errors="replace"))
    else:
        response_bytes = len(content) if content is not None else 0
    headers = getattr(response, "headers", {})
    content_type = str(headers.get("Content-Type", ""))[:120] if hasattr(headers, "get") else ""
    result = {
        **base,
        "http_status": status_code,
        "client_attempted": True,
        "client_attempts": 1,
        "response_bytes": response_bytes,
        "content_type": content_type,
        "elapsed_ms": elapsed_ms,
    }
    if status_code < 200 or status_code >= 300:
        result.update(
            {
                "state": "http_error",
                "stage": "http_response",
                "stop_family": status_code in (403, 429),
            }
        )
        if status_code in (403, 429):
            result["state"] = "rate_limited"
        return result

    try:
        payload = response.json()
    except (ValueError, json.JSONDecodeError):
        result.update(
            {
                "state": "invalid_payload",
                "stage": "payload_parse",
                "payload": {"format": "invalid_json"},
                "stop_family": False,
            }
        )
        return result

    result["payload"] = _shape_summary(payload)
    result["returned_data_dates"] = _response_data_dates(payload)
    state, reason = _contract_state(spec.contract, payload)
    result.update(
        {
            "state": state,
            "stage": "payload_contract",
            "reason": reason,
            "stop_family": False,
        }
    )
    return result


def _not_probed(spec: ProbeSpec, reason: str) -> dict[str, Any]:
    return {
        "name": spec.name,
        "risk_family": spec.risk_family,
        "host": spec.host,
        "path": spec.path,
        "requested_data_date": spec.requested_data_date,
        "state": "not_probed",
        "stage": "not_started",
        "client_attempted": False,
        "client_attempts": 0,
        "reason": reason,
        "stop_family": False,
    }


def run_probes(
    probes: list[ProbeSpec],
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    stopped_families: dict[str, str] = {}
    stop_all_reason: Optional[str] = None
    sent_any_request = False

    for spec in probes:
        if stop_all_reason:
            results.append(_not_probed(spec, stop_all_reason))
            continue
        if spec.risk_family in stopped_families:
            results.append(
                _not_probed(
                    spec,
                    f"risk family stopped after {stopped_families[spec.risk_family]}",
                )
            )
            continue
        if sent_any_request:
            sleep(INTER_PROBE_SECONDS)
        result = probe(spec)
        results.append(result)
        sent_any_request = sent_any_request or bool(result.get("client_attempted"))
        if result.get("stop_family"):
            stopped_families[spec.risk_family] = spec.name
        if result.get("state") == "diagnostic_error":
            stop_all_reason = f"diagnostic setup failed at {spec.name}"

    return results


def _run_state(results: list[dict[str, Any]]) -> str:
    states = {str(result.get("state")) for result in results}
    if states & _FAILURE_STATES:
        return "failed"
    if states & _INCONCLUSIVE_STATES:
        return "inconclusive"
    return "ok"


def _write_report(payload: dict[str, Any], output_path: Optional[Path]) -> Path:
    if output_path is None:
        stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
        output_path = ROOT / ".tmp" / "eastmoney_health" / f"{stamp}.json"
    elif not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def _format_result(result: dict[str, Any]) -> str:
    label = f"[{result['name']:<14}] {result['state']}"
    details = [f"{result['host']}{result['path']}"]
    if result.get("http_status") is not None:
        details.append(f"HTTP {result['http_status']}")
    details.append(f"attempted={'yes' if result.get('client_attempted') else 'no'}")
    if result.get("response_bytes") is not None:
        details.append(f"bytes={result['response_bytes']}")
    if result.get("elapsed_ms") is not None:
        details.append(f"{result['elapsed_ms']}ms")
    if result.get("failure_kind"):
        details.append(f"kind={result['failure_kind']}")
    if result.get("reason"):
        details.append(str(result["reason"]))
    return f"{label}: " + " | ".join(details)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="低频诊断东方财富接口可用性与响应结构")
    parser.add_argument("--once", action="store_true", help="只探测 push2 主域的 stock/get")
    parser.add_argument(
        "--probe",
        choices=("push2", "83.push2", "push2delay", "push2his", "push2ex", "datacenter-web"),
        help="只探测指定主机/接口",
    )
    parser.add_argument("--output", type=Path, help="诊断 JSON 输出路径，默认写入仓库 .tmp/")
    args = parser.parse_args(argv)
    if args.once and args.probe:
        parser.error("--once 与 --probe 不能同时使用")

    try:
        data_date = _latest_data_date()
        probes = _build_probes(data_date)
    except Exception as exc:
        print(f"无法确定交易数据日，未发送探测请求: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    if args.once:
        probes = probes[:1]
    elif args.probe:
        probes = [item for item in probes if item.name == args.probe]

    print(
        f"东方财富低频诊断：{len(probes)} 个所选端点 | 最近有效交易数据日 {data_date.isoformat()}"
    )
    print("同风险族遇到封禁或传输失败后停止探测；不重试，不绕过共享限流。")
    results = run_probes(probes)
    state = _run_state(results)
    report = {
        "schema_version": 1,
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "calendar_reference_date": data_date.isoformat(),
        "inter_probe_seconds": INTER_PROBE_SECONDS,
        "status": state,
        "probes": results,
    }
    report_path = _write_report(report, args.output)

    for result in results:
        print("  " + _format_result(result))
    print(f"诊断报告: {report_path}")
    if state == "failed":
        print("结果含有已实测失败；请按 host、path、stage 和响应结构定位，不要自动扩展重试。")
        return 1
    if state == "inconclusive":
        print("部分端点因本地熔断/封禁跳过或返回空数据；未测试项不代表接口失败。")
        return 2
    print("所选端点均返回符合预期的 JSON 结构。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
