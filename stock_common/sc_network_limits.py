"""Cross-process wait and lock mechanics used by the shared network client.

This module owns no limiter, endpoint, retry, or ban state. The facade passes its
single shared state and synchronization callbacks into these helpers.
"""

from __future__ import annotations

from typing import Any, Callable

DebugLog = Callable[[str], None]
FileLockAcquire = Callable[[str, float], bool]
FileLockRelease = Callable[[str], None]


def file_lock_acquire(
    lock_path: str,
    timeout: float,
    *,
    stale_seconds: float,
    os_module: Any,
    time_module: Any,
    debug_log: DebugLog,
) -> bool:
    """Acquire one shared lock file and reclaim stale locks after process crashes."""
    deadline = time_module.time() + timeout
    payload = f"{os_module.getpid()}|{time_module.time():.3f}"
    while time_module.time() < deadline:
        try:
            fd = os_module.open(lock_path, os_module.O_CREAT | os_module.O_EXCL | os_module.O_RDWR)
            try:
                os_module.write(fd, payload.encode("utf-8"))
            finally:
                os_module.close(fd)
            return True
        except FileExistsError:
            try:
                stat = os_module.stat(lock_path)
                if time_module.time() - stat.st_mtime > stale_seconds:
                    try:
                        os_module.remove(lock_path)
                        debug_log(f"file_lock_acquire: removed stale lock {lock_path}")
                        continue
                    except OSError:
                        pass
            except OSError:
                pass
            time_module.sleep(0.05)
        except Exception as exc:
            debug_log(f"file_lock_acquire error ({lock_path}): {exc}")
            return False
    return False


def file_lock_release(
    lock_path: str,
    *,
    os_module: Any,
    open_file: Callable[..., Any],
    debug_log: DebugLog,
) -> None:
    """Release a shared lock file only when its recorded owner is this process."""
    try:
        if os_module.path.exists(lock_path):
            try:
                with open_file(lock_path, "r", encoding="utf-8") as stream:
                    content = stream.read().strip()
                owner_pid = int(content.split("|")[0]) if content else -1
            except (OSError, ValueError):
                owner_pid = -1
            if owner_pid == os_module.getpid() or owner_pid == -1:
                os_module.remove(lock_path)
    except Exception as exc:
        debug_log(f"sc_network file_lock_release: {exc}")


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
    """Wait for a process-wide interval while preserving the legacy timestamp protocol."""
    waited = 0.0
    try:
        if use_lock and not file_lock_acquire(lock_file, target_interval + 5.0):
            return 0.0
        try:
            last_ts = 0.0
            if use_content_ts:
                try:
                    with open_file(lock_file, "r", encoding="utf-8") as stream:
                        content = stream.read().strip()
                    if content and "|" in content:
                        last_ts = float(content.split("|")[1])
                except (OSError, ValueError):
                    last_ts = 0.0
            elif os_module.path.exists(lock_file):
                last_ts = os_module.path.getmtime(lock_file)
            now = time_module.time()
            if last_ts > 0:
                elapsed = now - last_ts
                if elapsed < target_interval:
                    wait = target_interval - elapsed
                    time_module.sleep(wait)
                    waited = wait
            if use_content_ts:
                with open_file(lock_file, "w") as stream:
                    stream.write(f"{os_module.getpid()}|{time_module.time():.3f}")
            else:
                with open_file(lock_file, "w") as stream:
                    stream.write(str(time_module.time()))
        finally:
            if use_lock:
                file_lock_release(lock_file)
    except Exception as exc:
        debug_log(f"sc_network process_interval_wait: {exc}")
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
    """Reserve the next cross-process request slot for direct-client providers."""
    if not file_lock_acquire(lock_file, target_interval + 10.0):
        raise TimeoutError(f"provider rate-limit lock timed out: {lock_file}")
    waited = 0.0
    try:
        last_started = 0.0
        try:
            with open_file(state_file, "r", encoding="ascii") as state:
                last_started = float(state.read().strip())
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as exc:
            debug_log(f"provider_interval_wait invalid state ({state_file}): {exc}")

        now = time_module.time()
        remaining = target_interval - (now - last_started) if last_started > 0 else 0.0
        if remaining > 0:
            time_module.sleep(remaining)
            waited = remaining
        with open_file(state_file, "w", encoding="ascii") as state:
            state.write(f"{time_module.time():.6f}")
    finally:
        file_lock_release(lock_file)
    return waited
