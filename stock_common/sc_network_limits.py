"""Cross-process wait and lock mechanics used by the shared network client.

This module owns no limiter, endpoint, retry, or ban state. The facade passes its
single shared state and synchronization callbacks into these helpers.
"""

from __future__ import annotations

import math
import threading
from typing import Any, Callable

DebugLog = Callable[[str], None]
FileLockAcquire = Callable[[str, float], bool]
FileLockRelease = Callable[[str], None]

_LOCKS_GUARD = threading.Lock()
_LOCAL_LOCKS: dict[str, threading.Lock] = {}
_HELD_LOCKS: dict[tuple[int, str], tuple[threading.Lock, Any, str]] = {}


def _lock_path_key(lock_path: str, os_module: Any) -> str:
    return str(os_module.path.normcase(os_module.path.abspath(f"{lock_path}.mutex")))


def _acquire_os_lock(handle: Any, backend: str) -> None:
    handle.seek(0)
    if backend == "windows":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        return
    if backend == "posix":
        fcntl_module: Any = __import__("fcntl")

        fcntl_module.flock(handle.fileno(), fcntl_module.LOCK_EX | fcntl_module.LOCK_NB)
        return
    raise OSError(f"unsupported file-lock platform: {backend}")


def _release_os_lock(handle: Any, backend: str) -> None:
    handle.seek(0)
    if backend == "windows":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return
    if backend == "posix":
        fcntl_module: Any = __import__("fcntl")

        fcntl_module.flock(handle.fileno(), fcntl_module.LOCK_UN)
        return
    raise OSError(f"unsupported file-lock platform: {backend}")


def _process_next_allowed(content: str, interval: float, now: float) -> float:
    if content.startswith("v2|"):
        parts = content.split("|")
        if len(parts) != 2:
            raise ValueError(f"invalid process rate-limit state: {content!r}")
        next_allowed = float(parts[1])
    else:
        legacy_value = content.split("|", 1)[-1]
        last_started = float(legacy_value)
        if not math.isfinite(last_started) or last_started <= 0:
            raise ValueError(f"invalid process rate-limit timestamp: {content!r}")
        next_allowed = last_started + interval
    if not math.isfinite(next_allowed) or next_allowed <= 0:
        raise ValueError(f"invalid process rate-limit timestamp: {content!r}")
    if next_allowed - now > max(interval * 2.0, 2.0):
        raise ValueError(f"process rate-limit state is too far in the future: {content!r}")
    return next_allowed


def file_lock_acquire(
    lock_path: str,
    timeout: float,
    *,
    os_module: Any,
    time_module: Any,
    debug_log: DebugLog,
) -> bool:
    """Acquire a thread- and process-safe mutex released by the OS on process exit.

    The persistent ``.mutex`` file is only a lock target; rate-limit state remains in
    ``lock_path``. Keeping those files separate prevents state writes from invalidating
    the OS lock and removes unsafe stale-file reclamation races.
    """
    if not math.isfinite(timeout) or timeout < 0:
        raise ValueError(f"invalid file-lock timeout: {timeout!r}")

    key = _lock_path_key(lock_path, os_module)
    owner_key = (threading.get_ident(), key)
    with _LOCKS_GUARD:
        local_lock = _LOCAL_LOCKS.setdefault(key, threading.Lock())
    deadline = time_module.monotonic() + timeout
    if not local_lock.acquire(timeout=timeout):
        return False

    handle = None
    locked = False
    last_lock_error = None
    backend = (
        "windows"
        if os_module.name == "nt"
        else "posix" if os_module.name == "posix" else os_module.name
    )
    try:
        parent = os_module.path.dirname(key)
        if parent:
            os_module.makedirs(parent, exist_ok=True)
        handle = open(key, "a+b")
        handle.seek(0, os_module.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()

        attempted = False
        while not attempted or time_module.monotonic() < deadline:
            attempted = True
            try:
                _acquire_os_lock(handle, backend)
                with _LOCKS_GUARD:
                    _HELD_LOCKS[owner_key] = (local_lock, handle, backend)
                locked = True
                return True
            except OSError as exc:
                last_lock_error = exc
                remaining = deadline - time_module.monotonic()
                if remaining <= 0:
                    break
                time_module.sleep(min(0.05, remaining))
        if last_lock_error is not None:
            debug_log(f"file_lock_acquire timed out ({lock_path}): {last_lock_error}")
        return False
    except Exception as exc:
        debug_log(f"file_lock_acquire error ({lock_path}): {exc}")
        return False
    finally:
        if not locked:
            if handle is not None:
                try:
                    handle.close()
                except OSError as exc:
                    debug_log(f"file_lock_acquire close error ({lock_path}): {exc}")
            local_lock.release()


def file_lock_release(
    lock_path: str,
    *,
    os_module: Any,
    debug_log: DebugLog,
) -> None:
    """Release the OS mutex and local thread lock held by this thread."""
    key = _lock_path_key(lock_path, os_module)
    owner_key = (threading.get_ident(), key)
    with _LOCKS_GUARD:
        held = _HELD_LOCKS.pop(owner_key, None)
    if held is None:
        debug_log(f"file_lock_release without a matching acquire: {lock_path}")
        return

    local_lock, handle, backend = held
    release_error = None
    try:
        _release_os_lock(handle, backend)
    except Exception as exc:
        release_error = exc
        debug_log(f"file_lock_release unlock error ({lock_path}): {exc}")
    finally:
        try:
            handle.close()
        except Exception as exc:
            release_error = release_error or exc
            debug_log(f"file_lock_release close error ({lock_path}): {exc}")
        finally:
            local_lock.release()
    if release_error is not None and not handle.closed:
        raise RuntimeError(f"failed to release process lock: {lock_path}") from release_error


def process_interval_wait(
    lock_file: str,
    target_interval: float,
    use_lock: bool,
    use_content_ts: bool,
    *,
    file_lock_acquire: FileLockAcquire,
    file_lock_release: FileLockRelease,
    debug_log: DebugLog,
    os_module: Any,
    open_file: Callable[..., Any],
    time_module: Any,
) -> float:
    """Reserve a process-wide request slot and persist its next eligible timestamp.

    ``use_lock`` and ``use_content_ts`` remain accepted for callers of the old private
    helper. The implementation always takes the OS mutex and uses the versioned state
    format so no caller can accidentally select an uncoordinated path.
    """
    del use_lock, use_content_ts
    if not math.isfinite(target_interval) or target_interval < 0:
        raise ValueError(f"invalid process rate-limit interval: {target_interval!r}")

    waited = 0.0
    try:
        if not file_lock_acquire(lock_file, target_interval + 5.0):
            raise TimeoutError(f"process rate-limit lock timed out: {lock_file}")
        try:
            try:
                with open_file(lock_file, "r", encoding="utf-8") as stream:
                    content = stream.read().strip()
            except FileNotFoundError:
                content = ""
            now = time_module.time()
            if content:
                next_allowed = _process_next_allowed(content, target_interval, now)
            elif os_module.path.exists(lock_file):
                raise ValueError(f"empty process rate-limit state: {lock_file}")
            else:
                next_allowed = 0.0

            while next_allowed > 0:
                remaining = next_allowed - time_module.time()
                if remaining <= 0:
                    break
                time_module.sleep(remaining)
                waited += remaining

            with open_file(lock_file, "w", encoding="utf-8") as stream:
                next_allowed = time_module.time() + target_interval
                stream.write(f"v2|{next_allowed:.9f}")
        finally:
            file_lock_release(lock_file)
    except Exception as exc:
        debug_log(f"sc_network process_interval_wait: {exc}")
        raise
    return waited


def provider_interval_wait(
    lock_file: str,
    state_file: str,
    target_interval: float,
    *,
    file_lock_acquire: FileLockAcquire,
    file_lock_release: FileLockRelease,
    debug_log: DebugLog,
    open_file: Callable[..., Any],
    time_module: Any,
) -> float:
    """Wait before a direct-client request and fail closed on invalid shared state."""
    if not math.isfinite(target_interval) or target_interval < 0:
        raise ValueError(f"invalid provider rate-limit interval: {target_interval!r}")
    if not file_lock_acquire(lock_file, target_interval + 10.0):
        raise TimeoutError(f"provider rate-limit lock timed out: {lock_file}")
    waited = 0.0
    try:
        last_started = 0.0
        state_missing = False
        try:
            with open_file(state_file, "r", encoding="ascii") as state:
                raw_state = state.read().strip()
        except FileNotFoundError:
            raw_state = ""
            state_missing = True
        except OSError as exc:
            debug_log(f"provider_interval_wait unreadable state ({state_file}): {exc}")
            raise

        if raw_state:
            try:
                last_started = float(raw_state)
            except ValueError as exc:
                debug_log(f"provider_interval_wait invalid state ({state_file}): {exc}")
                raise ValueError(f"invalid provider rate-limit state: {state_file}") from exc
            if not math.isfinite(last_started) or last_started <= 0:
                raise ValueError(f"invalid provider rate-limit timestamp: {raw_state!r}")
        elif not state_missing:
            raise ValueError(f"empty provider rate-limit state: {state_file}")

        now = time_module.time()
        if last_started > 0 and last_started - now > max(target_interval * 2.0, 2.0):
            raise ValueError(f"provider rate-limit state is too far in the future: {raw_state!r}")
        if last_started > 0:
            while True:
                remaining = target_interval - (time_module.time() - last_started)
                if remaining <= 0:
                    break
                time_module.sleep(remaining)
                waited += remaining
        with open_file(state_file, "w", encoding="ascii") as state:
            state.write(f"{time_module.time():.9f}")
    finally:
        file_lock_release(lock_file)
    return waited
