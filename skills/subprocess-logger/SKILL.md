---
name: subprocess-logger
description: >
  Subprocess logging & Windows stdout flushing rules for main.py / gd_uploader.py /
  report runner scripts. Use this skill whenever the user is editing
  `asyncio.create_subprocess_exec`, debugging "子进程输出被吞", "stdout 缓冲",
  "GD 上传无日志", or "input 卡住" in non-interactive mode. Trigger on phrases
  like "flush=True", "stdout=PIPE", "isatty", "非交互模式", "GD 日志被吞",
  "子进程接管输出".
version: 1.0.0
---

# Subprocess Logger Guidelines

V15.2 GD 上传缓冲修复后的强约束规则集。解决 3 类 Windows 子进程日志问题：
1. **stdout 缓冲被吞**：`asyncio.create_subprocess_exec(..., stdout=None)` 在 Windows 等价于继承父进程控制台，子进程 print 走全缓冲
2. **`input()` 卡住**：main.py 子进程 stdin=None 时，`init_gd` 的 `input()` 永久等待
3. **UnicodeEncodeError**：Windows GBK 控制台打印 emoji 报错

## Rule 1: Always Use `flush=True` for Progress Prints

All console `print(...)` calls in runner scripts (`BaseReportRunner`), data providers, and upload routines MUST include `flush=True` so that outputs are instantly delivered to parent process stdout when invoked via `asyncio.create_subprocess_exec` on Windows.

```python
# GOOD: guaranteed instant stdout delivery
print("  ✅ Google Drive 认证成功", flush=True)
print(f"  ⚠️ GD 连接失败 ({attempt+1}/{max_retry})", flush=True)
print(f"✔ [{label}] {script} 完成 ({dt:.1f}s)", flush=True)

# BAD: stdout 缓冲（Windows 全缓冲 4KB，子进程日志被吞）
print("  ✅ Google Drive 认证成功")
```

## Rule 2: `main.py` Subprocess MUST Use `stdout=PIPE` + Async Drain

In `main.py`, the `asyncio.create_subprocess_exec(...)` call MUST use `stdout=asyncio.subprocess.PIPE` + `stderr=asyncio.subprocess.STDOUT` + an async `readline()` drain task — never `stdout=None` (which inherits parent control and is fully buffered on Windows).

**Why**: `stdout=None` 在 Windows 上等价于父进程控制台，但控制台缓冲 4KB，subprocess print 在 4KB 以下的内容不显示，直到子进程结束才一次性 flush —— 表现为"子进程跑完才看到日志"。

```python
# GOOD: PIPE + async drain (main.py)
async def _run_script_async(script, stock_codes, output_dir, no_upload, label):
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=_SCRIPT_DIR,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    # 异步实时打印子进程输出（解决 Windows 缓冲问题）
    async def _drain_output():
        if proc.stdout is None:
            return
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            try:
                print(line.decode("utf-8", errors="replace").rstrip(), flush=True)
            except UnicodeDecodeError:
                print(line.decode("gbk", errors="replace").rstrip(), flush=True)

    drain_task = asyncio.create_task(_drain_output())
    try:
        rc = await asyncio.wait_for(proc.wait(), timeout=1800)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        drain_task.cancel()
        return script, -1, time.time() - t0, label
    # 等待输出排空
    try:
        await asyncio.wait_for(drain_task, timeout=5)
    except asyncio.TimeoutError:
        drain_task.cancel()
    return script, rc, time.time() - t0, label

# BAD: stdout=None (Windows 缓冲，子进程日志被吞)
proc = await asyncio.create_subprocess_exec(*cmd, stdout=None, stderr=None)
```

## Rule 3: `init_gd` MUST Detect Non-Interactive Mode via `sys.stdin.isatty()`

In `gd_uploader.py`, the `init_gd()` function MUST check `sys.stdin.isatty()` BEFORE the `input()` loop. If `False` (main.py 子进程 stdin=None / 管道), return `skip_upload=True` immediately.

**Why**: main.py 子进程 stdin=None，`input()` 在 EOFError 时抛异常；但抛异常前会无限等待。`isatty()` 提前检测跳过整个交互。

```python
# GOOD: isatty 跳过非交互模式 (gd_uploader.py)
def init_gd(base_dir, ...):
    drive, proxy_set = None, False

    # V15.2: 检测非交互模式（main.py 子进程 stdin=None / 管道），
    # 跳过 input() 等待，避免卡住后台批量运行
    import sys
    if not sys.stdin.isatty():
        print("  ℹ️ 检测到非交互模式（stdin 非 tty），自动跳过云端上传", flush=True)
        return None, False, None, True

    # 交互式连接
    while True:
        try:
            drive, proxy_set = init_google_drive(base_dir)
            if drive:
                return drive, proxy_set, None, False
        except Exception as e:
            print(f"  ⚠️ GD 连接异常: {e}", flush=True)

        try:
            choice = input("请选择 [2]: ").strip() or "2"
        except (EOFError, KeyboardInterrupt):
            return None, proxy_set, None, True  # Ctrl+C / EOF
        # ... 重试逻辑
```

## Rule 4: Wrap Console Unicode in `try/except UnicodeEncodeError`

Always wrap console unicode characters (e.g. `🚀`, `⏱`, `✅`, `⚠️`) with `try...except UnicodeEncodeError` to handle non-UTF-8 Windows consoles safely.

```python
# GOOD: GBK fallback
try:
    print("  ✅ 启动完成", flush=True)
except UnicodeEncodeError:
    print("  [OK] 启动完成", flush=True)
```

## Rule 5: `init_gd` Auto-Retry 3 Times

The `init_gd()` function MUST auto-retry 3 times with increasing intervals (3s → 6s) before prompting the user. This reduces user friction on transient network blips.

```python
def retry_get_folder_interactive(drive, folder_name, parent_folder_id,
                                 max_auto_retry: int = 3) -> Optional[str]:
    for attempt in range(max_auto_retry):
        try:
            return drive.CreateFile(...)
        except Exception as e:
            if attempt < max_auto_retry - 1:
                wait_time = 3 * (attempt + 1)
                print(f"  ⏳ {wait_time} 秒后自动重试 ({attempt + 2}/{max_auto_retry})…",
                      flush=True)
                time.sleep(wait_time)
            else:
                print(f"  ⚠️ GD 云端同步跳过 (重试 {max_auto_retry} 次后失败): {e}",
                      flush=True)
                return None
```

## Output format

```python
# Standard main.py subprocess pattern
proc = await asyncio.create_subprocess_exec(
    *cmd,
    cwd=_SCRIPT_DIR,
    stdout=asyncio.subprocess.PIPE,        # V15.2: NOT None
    stderr=asyncio.subprocess.STDOUT,
)
# 异步 drain 任务（必须）
drain_task = asyncio.create_task(_drain_output())
rc = await asyncio.wait_for(proc.wait(), timeout=1800)
await asyncio.wait_for(drain_task, timeout=5)  # 排空
```

## Examples

**Example 1** (V15.2 真实事故)
Input: 用户报 "val 报告 1000s 跑完但 GD 上传无日志"
Action:
1. `main.py` L267-268 `stdout=None` 改为 `stdout=asyncio.subprocess.PIPE`
2. 增加 `_drain_output` 异步 task
3. 验证 `python main.py --val 300750` 日志实时输出
Output: GD 上传日志实时显示

**Example 2** (init_gd 卡住)
Input: 用户报 "main.py 子进程卡在 GD 上传"
Action: `gd_uploader.py` `init_gd` 入口增加 `sys.stdin.isatty()` 检测

**Example 3** (UnicodeEncodeError on Windows)
Input: 用户报 "GBK 控制台打印 emoji 崩溃"
Action: 所有 emoji print 加 `try/except UnicodeEncodeError` 包装

## Submission Checklist

- [ ] 所有 `print(...)` 加 `flush=True`
- [ ] `main.py` subprocess 用 `stdout=PIPE` + `_drain_output` 异步排空
- [ ] `gd_uploader.py` `init_gd` 用 `sys.stdin.isatty()` 检测
- [ ] emoji print 加 `try/except UnicodeEncodeError` 包装
- [ ] `init_gd` 自动重试 3 次（3s/6s 间隔）

## Reference Files

- `references/windows_subprocess_patterns.md` — Windows asyncio 子进程 stdout 缓冲原理
- `references/gd_upload_retry.md` — GD 自动重试 + 用户手动选择流程图
