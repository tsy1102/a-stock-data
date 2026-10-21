"""Eastmoney datacenter endpoint implementation.

The public compatibility surface and dependency injection points remain in
``_eastmoney``. This module owns only the stateless request/response handling
for the synchronous and asynchronous datacenter endpoints; rate limiting,
retry policy, cache state, and endpoint consumers stay with their existing
owners.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List


def query_datacenter(
    code: str,
    report_name: str,
    columns: str,
    filter_str: str,
    page_size: int,
    sort_columns: str,
    sort_types: str,
    page_index: int,
    *,
    quick_request: Callable[..., Any],
    datacenter_url: str,
    user_agent: str,
    http_logger: Any,
    biz_logger: Any,
    debug_log: Callable[[str], Any],
) -> List[Dict[str, Any]]:
    """Run one synchronous datacenter request and normalize its row list."""
    try:
        # V17.4.1: market-level reports with no explicit filter request all rows.
        full_filter = filter_str if filter_str else (f'(SECURITY_CODE="{code}")' if code else "")
        response = quick_request(
            datacenter_url,
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
            headers={"User-Agent": user_agent},
            timeout=15,
        )
        if response is None:
            return []
        if response.status_code != 200:
            http_logger.error(f"{response.status_code} | {datacenter_url} | {report_name} | {code}")
            return []
        try:
            payload = response.json()
        except Exception as json_error:
            http_logger.error(
                f"JSONDecodeError | {datacenter_url} | {report_name} | {code} | {json_error}"
            )
            return []
        if isinstance(payload, dict) and payload.get("status") == -1:
            biz_logger.error(f"status=-1 | {report_name} | {code} | {payload.get('message', '')}")
            return []
        if isinstance(payload, dict):
            result = payload.get("result")
            if isinstance(result, dict):
                data = result.get("data")
                if isinstance(data, list):
                    return [row for row in data if isinstance(row, dict)]
        return []
    except Exception as error:
        debug_log(f"eastmoney_datacenter({code}, {report_name}): {error}")
        return []


async def query_datacenter_async(
    session: Any,
    code: str,
    report_name: str,
    columns: str,
    filter_str: str,
    page_size: int,
    sort_columns: str,
    sort_types: str,
    *,
    async_request_with_retry: Callable[..., Awaitable[Any]],
    datacenter_url: str,
    user_agent: str,
    biz_logger: Any,
    debug_log: Callable[[str], Any],
) -> List[Dict[str, Any]]:
    """Run one asynchronous datacenter request and normalize its row list."""
    try:
        # V17.4.1: same market-level empty-filter behavior as the sync endpoint.
        full_filter = filter_str if filter_str else (f'(SECURITY_CODE="{code}")' if code else "")
        payload = await async_request_with_retry(
            session,
            datacenter_url,
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
            headers={"User-Agent": user_agent},
            timeout=15,
        )
        if payload is None:
            return []
        if isinstance(payload, dict) and payload.get("status") == -1:
            biz_logger.error(f"status=-1 | {report_name} | {code} | {payload.get('message', '')}")
            return []
        if isinstance(payload, dict):
            result = payload.get("result")
            if isinstance(result, dict):
                data = result.get("data")
                if isinstance(data, list):
                    return [row for row in data if isinstance(row, dict)]
        return []
    except Exception as error:
        debug_log(f"eastmoney_datacenter_async({code}, {report_name}): {error}")
        return []
