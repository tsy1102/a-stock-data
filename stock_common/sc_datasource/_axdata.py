"""Public AxData request adapter used by project collectors.

AxData is an interface aggregation framework, so callers must name the
interface and its actual upstream family. Requests through this wrapper are
read-only, uncached, and never retried here.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def get_axdata_records(
    interface: str,
    *,
    params: Mapping[str, Any] | None = None,
    fields: str | Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    """Return one normalized AxData response without persistence or retries."""
    if not isinstance(interface, str) or not interface.strip():
        raise ValueError("AxData interface must be a non-empty string")

    from axdata_core import request_interface

    response = request_interface(
        interface,
        params=params,
        fields=fields,
        persist=False,
    )
    records = getattr(response, "records", None)
    if not isinstance(records, list):
        raise TypeError(f"AxData {interface} response records must be a list")
    if any(not isinstance(record, dict) for record in records):
        raise TypeError(f"AxData {interface} response contains a non-object record")
    return records


__all__ = ["get_axdata_records"]
