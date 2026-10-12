"""Run one bounded Levistock API sample per completed trading date.

Candidate calls are opt-in at the capture integration point, rate-limited by
their real provider family, and never treated as independent source anchors.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import date, datetime
from importlib import metadata
from pathlib import Path
from typing import Any, Callable, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = PROJECT_ROOT / ".tmp" / "a_stock_data_v7" / "levistock_daily_probe_state.json"
LOCK_DIR = PROJECT_ROOT / ".tmp" / "a_stock_data_v7" / "locks"
EXPECTED_PACKAGE_VERSION = "0.1.8"
_BLOCK_PATTERN = re.compile(
    r"\b403\b|\b429\b|blocked|banned|rate.?limit|封禁|限流|访问频繁", re.IGNORECASE
)
_ERROR_KEYS = frozenset({"__error__", "__skipped__"})

# Each entry makes one upstream API request. Keep this list limited to numeric,
# field-bearing methods that can help compare source contracts. Text/news/hot-list
# and Eastmoney methods are intentionally excluded (see the reconciliation report).
CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "id": "cls_sector_industry",
        "adapter": "levistock.sector.sector_cls.sector_industry_cls",
        "provider_family": "cls",
        "needs_stock": False,
        "date_basis": "live_snapshot",
    },
    {
        "id": "kph_market_emotion",
        "adapter": "levistock.market.market_emotion_kph.market_emotion_kph",
        "provider_family": "kph",
        "needs_stock": False,
        "date_basis": "requested_trade_date",
    },
    {
        "id": "cls_sector_heat",
        "adapter": "levistock.sector.sector_heat_cls.get_sector_heat",
        "provider_family": "cls",
        "needs_stock": False,
        "date_basis": "live_snapshot",
    },
    {
        "id": "kph_sector_ranking",
        "adapter": "levistock.sector.sector_ranking_kph.sector_ranking_kph",
        "provider_family": "kph",
        "needs_stock": False,
        "date_basis": "requested_trade_date",
    },
    {
        "id": "cls_sector_rotation",
        "adapter": "levistock.sector.sector_rotation_cls.get_sector_rotation",
        "provider_family": "cls",
        "needs_stock": False,
        "date_basis": "response_trade_dates",
    },
    {
        "id": "cls_stock_kline",
        "adapter": "levistock.stock.stock_kline_cls.stock_kline_cls",
        "provider_family": "cls",
        "needs_stock": True,
        "date_basis": "response_trade_dates",
    },
    {
        "id": "cls_stock_timeline",
        "adapter": "levistock.stock.stock_kline_cls.stock_timeline_cls",
        "provider_family": "cls",
        "needs_stock": True,
        "date_basis": "response_trade_date",
    },
)


def _date_key(value: Any) -> Optional[str]:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    for pattern in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(normalized, pattern).date().isoformat()
        except ValueError:
            continue
    return None


def _has_data(value: Any) -> bool:
    if isinstance(value, dict):
        return any(key not in _ERROR_KEYS and _has_data(child) for key, child in value.items())
    if isinstance(value, (list, tuple)):
        return any(_has_data(item) for item in value)
    return value is not None and value != ""


def _error_is_blocked(value: Any) -> bool:
    return bool(_BLOCK_PATTERN.search(str(value or "")))


def _error_status(exc: Exception) -> Optional[int]:
    response = getattr(exc, "response", None)
    candidates = (getattr(response, "status_code", None), getattr(exc, "status_code", None))
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            status = int(candidate)
        except (TypeError, ValueError):
            continue
        if status in {403, 429}:
            return status
    match = re.search(r"\b(403|429)\b", str(exc))
    return int(match.group(1)) if match else None


def _read_state(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"schema_version": 1, "next_candidate_index": 0, "blocked_families": []}
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"probe_state_unreadable:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise ValueError("probe_state_root_is_not_object")
    return value


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def _acquire_lock(target_date: str) -> Optional[Path]:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = LOCK_DIR / f"levistock_daily_probe_{target_date.replace('-', '')}.lock"
    try:
        descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        try:
            if time.time() - lock_path.stat().st_mtime > 1800:
                lock_path.unlink()
                descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            else:
                return None
        except (FileNotFoundError, FileExistsError, OSError):
            return None
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write(f"pid={os.getpid()}\nstarted={time.time():.3f}\n")
    except OSError:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return lock_path


def _release_lock(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _counterpart_status(family: str, market_data: dict[str, Any]) -> tuple[bool, str, bool]:
    key = "cls_market_emotion" if family == "cls" else "kph_limit_ladder"
    payload = market_data.get(key)
    if isinstance(payload, dict) and "__error__" in payload:
        error = str(payload["__error__"])
        return False, f"counterpart_failed:{key}", _error_is_blocked(error)
    if isinstance(payload, dict) and "__skipped__" in payload:
        return False, f"counterpart_skipped:{key}", False
    if not _has_data(payload):
        return False, f"counterpart_empty:{key}", False
    return True, "ok", False


def _provider_is_blocked(family: str) -> bool:
    from stock_common.sc_network import _levistock_provider_is_blocked

    return _levistock_provider_is_blocked(family)


def _mark_provider_block(family: str, error: Exception) -> bool:
    from stock_common.sc_network import _mark_levistock_provider_block

    return _mark_levistock_provider_block(family, error)


def _stock_code(pool: list[dict[str, Any]]) -> Optional[str]:
    codes = sorted(
        {
            re.sub(r"\D", "", str(item.get("code") or ""))[-6:]
            for item in pool
            if isinstance(item, dict)
            and len(re.sub(r"\D", "", str(item.get("code") or ""))[-6:]) == 6
        }
    )
    return codes[0] if codes else None


def _request_candidate(
    candidate_id: str,
    target_date: str,
    stock_code: Optional[str],
    expected_family: str,
) -> tuple[Any, dict[str, Any], str]:
    from stock_common.sc_datasource import get_levistock_candidate_sample

    return get_levistock_candidate_sample(
        candidate_id,
        data_date=target_date,
        stock_code=stock_code,
        expected_family=expected_family,
    )


def run_levistock_daily_probe(
    *,
    out_dir: str | Path,
    data_date: Any,
    latest_completed_trade_date: Any,
    data_date_domain: str,
    market_phase: str,
    only: str | None,
    market_data: dict[str, Any],
    pool: list[dict[str, Any]],
    now: Optional[datetime] = None,
    state_path: Optional[str | Path] = None,
    candidate_requester: Optional[Callable[..., tuple[Any, dict[str, Any], str]]] = None,
) -> dict[str, Any]:
    """Collect one safe candidate response or return an explicit skip/error record."""
    output_dir = Path(out_dir)
    target_date = _date_key(data_date)
    latest_date = _date_key(latest_completed_trade_date)
    evaluated_at = now or datetime.now().astimezone()
    result: dict[str, Any] = {
        "status": "skipped",
        "candidate_id": None,
        "provider_family": None,
        "adapter": None,
        "data_date": target_date,
        "package": "levistock",
        "package_version": None,
        "expected_package_version": EXPECTED_PACKAGE_VERSION,
        "version_matches_requirement": False,
        "request_count": 0,
        "payload": {"__skipped__": "not_eligible"},
    }
    selected = {part.strip() for part in (only or "").split(",") if part.strip()}
    reason = None
    if selected and "market_sources" not in selected:
        reason = "market_sources_not_selected"
    elif data_date_domain not in {"trading", "trading_day"}:
        reason = "capture_date_is_not_a_trading_day"
    elif market_phase != "closed":
        reason = "capture_is_not_a_closed_market_snapshot"
    elif target_date is None or latest_date is None or target_date != latest_date:
        reason = "capture_is_not_the_latest_completed_trading_day"
    if reason:
        result["reason"] = reason
        result["payload"] = {"__skipped__": reason}
        return result
    if target_date is None:
        reason = "capture_is_not_the_latest_completed_trading_day"
        result.update(reason=reason, payload={"__skipped__": reason})
        return result

    try:
        package_version = metadata.version("levistock")
    except metadata.PackageNotFoundError:
        result.update(
            reason="levistock_not_installed", payload={"__skipped__": "levistock_not_installed"}
        )
        return result
    result["package_version"] = package_version
    result["version_matches_requirement"] = package_version == EXPECTED_PACKAGE_VERSION

    candidate_file = output_dir / "levistock_candidate_raw.json"
    if candidate_file.exists():
        try:
            existing = json.loads(candidate_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = None
        if isinstance(existing, dict) and existing.get("data_date") == target_date:
            result.update(
                status="already_recorded",
                reason="candidate_sample_already_exists_for_data_date",
                candidate_id=(existing.get("probe") or {}).get("candidate_id"),
                provider_family=(existing.get("probe") or {}).get("provider_family"),
                adapter=(existing.get("probe") or {}).get("adapter"),
                request_count=0,
                payload={"__skipped__": "candidate_sample_already_exists_for_data_date"},
            )
            return result

    if not result["version_matches_requirement"]:
        reason = "installed_package_version_does_not_match_requirement"
        result.update(status="skipped", reason=reason, payload={"__skipped__": reason})
        return result

    target_state_path = Path(state_path) if state_path else STATE_PATH
    try:
        lock_path = _acquire_lock(target_date or "unknown")
    except OSError as exc:
        result.update(status="failed_open", reason=f"probe_lock_error:{type(exc).__name__}")
        result["payload"] = {"__error__": result["reason"]}
        return result
    if lock_path is None:
        result.update(status="skipped", reason="another_probe_holds_daily_lock")
        result["payload"] = {"__skipped__": result["reason"]}
        return result

    try:
        try:
            state = _read_state(target_state_path)
        except ValueError as exc:
            result.update(status="failed_open", reason=str(exc), payload={"__error__": str(exc)})
            return result

        if state.get("last_attempted_data_date") == target_date:
            result.update(
                status="already_recorded",
                reason="attempt_already_made_for_data_date",
                candidate_id=state.get("last_candidate_id"),
                provider_family=state.get("last_provider_family"),
                adapter=state.get("last_adapter"),
                request_count=0,
                payload={"__skipped__": "attempt_already_made_for_data_date"},
            )
            return result

        blocked = set(state.get("blocked_families", []))
        for family in ("cls", "kph"):
            try:
                if _provider_is_blocked(family):
                    blocked.add(family)
            except Exception as exc:
                blocked.update({"cls", "kph"})
                state["last_outcome"] = "provider_block_state_unreadable"
                state["last_error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
                _write_state(target_state_path, state)
                result.update(
                    status="failed_open",
                    reason="provider_block_state_unreadable_fail_closed",
                    payload={"__error__": state["last_error"]},
                )
                return result
        start_index = int(state.get("next_candidate_index", 0)) % len(CANDIDATES)
        chosen_index = None
        chosen_code = _stock_code(pool)
        skip_reasons: list[str] = []
        for offset in range(len(CANDIDATES)):
            index = (start_index + offset) % len(CANDIDATES)
            candidate = CANDIDATES[index]
            family = str(candidate["provider_family"])
            if family in blocked:
                skip_reasons.append(f"{family}_blocked_until_manual_review")
                continue
            if candidate["needs_stock"] and not chosen_code:
                skip_reasons.append("no_stock_probe_candidate")
                continue
            counterpart_ok, counterpart_reason, counterpart_blocked = _counterpart_status(
                family, market_data
            )
            if not counterpart_ok:
                skip_reasons.append(counterpart_reason)
                if counterpart_blocked:
                    blocked.add(family)
                continue
            chosen_index = index
            break

        if chosen_index is None:
            state.update(
                last_evaluated_data_date=target_date,
                last_outcome="no_eligible_candidate",
                blocked_families=sorted(blocked),
            )
            _write_state(target_state_path, state)
            reason = ";".join(sorted(set(skip_reasons))) or "no_candidate_available"
            result.update(status="skipped", reason=reason, payload={"__skipped__": reason})
            return result

        candidate = CANDIDATES[chosen_index]
        family = str(candidate["provider_family"])
        state.update(
            last_attempted_data_date=target_date,
            last_candidate_id=candidate["id"],
            last_provider_family=family,
            last_adapter=candidate["adapter"],
            next_candidate_index=(chosen_index + 1) % len(CANDIDATES),
            blocked_families=sorted(blocked),
            last_outcome="request_started",
        )
        _write_state(target_state_path, state)

        result.update(
            candidate_id=candidate["id"],
            provider_family=family,
            adapter=candidate["adapter"],
            date_basis=candidate["date_basis"],
            stock_code=chosen_code if candidate["needs_stock"] else None,
        )
        try:
            requester = candidate_requester or _request_candidate
            payload, params, adapter = requester(
                str(candidate["id"]),
                target_date,
                chosen_code if candidate["needs_stock"] else None,
                family,
            )
            result["request_count"] = 1
            if adapter != candidate["adapter"]:
                raise RuntimeError("candidate_adapter_mapping_mismatch")
            result["request_params"] = params
            if not _has_data(payload):
                result.update(status="empty", reason="empty_candidate_response")
                result["payload"] = {"__error__": "empty candidate response"}
            else:
                result.update(status="observed", payload=payload)
            state["last_outcome"] = result["status"]
            state.pop("last_error", None)
        except Exception as exc:
            if getattr(exc, "request_started", False):
                result["request_count"] = 1
            blocked_status = _error_status(exc)
            blocked_error = blocked_status is not None or _error_is_blocked(exc)
            if blocked_error:
                blocked.add(family)
                try:
                    _mark_provider_block(family, exc)
                except Exception as block_exc:
                    state["block_persistence_error"] = (
                        f"{type(block_exc).__name__}: {str(block_exc)[:120]}"
                    )
            state.update(
                last_outcome="blocked" if blocked_error else "error",
                last_error=f"{type(exc).__name__}: {str(exc)[:180]}",
                blocked_families=sorted(blocked),
            )
            result.update(
                status="blocked" if blocked_error else "error",
                reason="provider_rate_limited" if blocked_error else "candidate_request_failed",
                error=state["last_error"],
            )
            result["payload"] = {"__error__": state["last_error"]}
        raw_record = {
            "schema_version": "1.0",
            "data_date": target_date,
            "evaluated_at": evaluated_at.isoformat(timespec="seconds"),
            "probe": {key: value for key, value in result.items() if key != "payload"},
            "payload": result["payload"],
        }
        candidate_path = output_dir / "levistock_candidate_raw.json"
        temporary_path = candidate_path.with_suffix(candidate_path.suffix + ".tmp")
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(
                json.dumps(raw_record, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            os.replace(temporary_path, candidate_path)
        except OSError as exc:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
            except OSError as cleanup_exc:
                logging.getLogger(__name__).warning(
                    "Could not remove temporary Levistock evidence %s: %s",
                    temporary_path,
                    cleanup_exc,
                )
            state["last_outcome"] = "evidence_write_failed"
            state["last_error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
            _write_state(target_state_path, state)
            result.update(
                status="failed_open",
                reason="candidate_evidence_write_failed",
                error=f"{type(exc).__name__}: {str(exc)[:160]}",
            )
            return result
        _write_state(target_state_path, state)
        return result
    finally:
        _release_lock(lock_path)
