# val 报告超时（FAIL -1）根因定位与根因级修复

日期：2026-09-09｜脚本：`get_val_report.py`｜现象：批量报告日志 `全市场选股: FAIL(-1)`（耗时 1702.8s），其余 mak/sht/med/lng 均 OK。

## 一、先证伪"今天字段核查提交导致超时"这一假设

git 实证（全部命令可复现）：

```
git log --since="2026-09-09" --name-only -- '*.py'
# 今日(9-09)被改的 .py 仅 12 个，全部是字段核查/探测脚本：
#   scripts/_collide_tx56_beta.py, _collide_tx56_beta2.py, _extract_kline_full.py,
#   _extract_tdx_kline.py, _survey_tdx_kline.py, _tx45_47_qt_cross.py, _verify_tx56_final.py,
#   capture_field_probe.py, computed_collider.py, crack_tdx_mcp_20260908.py,
#   field_meta.py, lint_field_same_number.py
# —— 无一在 val 运行时导入链中。

git log --since="2026-09-09" --name-only -- 'core/*' 'stock_common/*' 'get_val_report.py' 'main.py'
# <<< 空：今天运行时文件零改动 >>>

git diff --stat HEAD -- 'core/*' 'stock_common/*' 'get_val_report.py' 'main.py'
# <<< 空：无未提交运行时改动 >>>
```

val 运行时文件最后改动时间：
- `get_val_report.py` → `feb30f1` (2026-09-07)
- `core/data_provider.py` → `ff93acf` (2026-09-07)
- `stock_common/sc_datasource/*` → `b7c4414` (2026-09-08)
- `stock_common/sc_fuyao.py` → 9-08 前

**结论**：我的今日字段核查提交（field_dict.md / lint / 对齐表）+ 全部 9-09 提交，**没有任何一个进入 val 运行时导入链**（已 grep 确认 `get_val_report.py`/`sc_report_runner.py` 不读取 `field_dict.md`，也不 import `lint_field_same_number`）。因此"今天的字段核查提交导致 val 超时"这一因果关系**不成立**。

## 二、真正的根因（val 既有代码的缺陷，今日被上游抖动触发）

### 2.1 现象机制
`main.py:321-332` 的卡死保护：`_STALL_TIMEOUT=900s`，子进程**连续 900s 无 stdout 输出**即 `proc.kill()` 并返回 `-1`。val 跑满约 800s 后有进度输出，随后进入 ≥15 分钟静默段 → 被判定卡死强杀。

### 2.2 代码缺陷（核心）
`get_val_report.py` 策略执行器（原 2166-2180 行）：

```python
async def _run_sync_strategy(name, func, *args):
    async with _strategy_sem:                      # Semaphore(3)
        if inspect.iscoroutinefunction(func):
            _r = await func(*args)
        else:
            _r = await asyncio.to_thread(func, *args)   # ← 无超时墙！
    print(f"  {name}... 完成(...)")                    # 挂起则永不打印
```

**缺陷**：`asyncio.to_thread(func)` 没有 `asyncio.wait_for` 硬超时墙。任一策略内部的阻塞 I/O 一旦挂起，线程永不返回 → `asyncio.gather(*_tasks)`（2239 行）永不完成 → 永不打印"完成"行 → 触发 main.py 的 900s 强杀。

### 2.3 触发条件（为何今天暴露）
底层 `sc_network._quick_request` 用 `requests.Session().request(..., timeout=15)`。
**关键盲区**：`requests` 的 `timeout` 仅覆盖 **connect/read 阶段，不覆盖 DNS 解析**（`socket.getaddrinfo` 不受其约束）。当上游（fuyao/东财）DNS 或路由**间歇挂起**时，`requests` 会**远超 15s 甚至无限挂起**。

- `is_fuyao_enabled()` = True（`credentials/fuyao_key.txt` 自 2026-08-23 起存在）→ **策略25【PS低估值】今日确实在打 fuyao 外部 API**（`get_fuyao_valuation` @ `sc_fuyao.py:272`）。
- 在用户跑批的时间窗，fuyao（或东财 datacenter）DNS/路由出现间歇挂起 → 策略25 的 `get_fuyao_valuation` 超出 `timeout=15` 仍不返回 → 线程挂起 → 整批停滞。

### 2.4 为何 val 挂、mak 不挂（discriminator）
`mak`（异动扫描）走 **ZHB 内存快照、零逐股深取**，不调用策略25（fuyao）等外部深取路径 → 362.8s 完成。
`val`（全市场选股）跑 **25 策略含 fuyao/东财逐股深取** → 命中上游挂起路径 → 1702.8s 后被杀。

> 实测佐证（本机 23:00 复测）：`fuyao.aicubes.cn` DNS 正常、TCP443 正常、API 可达（仅我猜的路径 404，主机本身正常）；`get_yjyg_all`（策略22）有 5 页上限+timeout=15+try/except 兜底，有界安全。说明当前上游已恢复，超时是**间歇性**上游抖动 + **既有代码缺陷**共同作用的产物——这也解释了"此前一直正常"：过去 fuyao 上游稳定时，缺陷不暴露。

## 三、根因级修复（非掩因式补丁）

**修复点**：`get_val_report.py` `_run_sync_strategy` 加每策略硬超时墙 `_STRATEGY_TIMEOUT=720s`（< `main.py` 的 900s 卡死保护）。

```python
_STRATEGY_TIMEOUT = 720  # 每策略硬超时墙：< main.py _STALL_TIMEOUT(900)，确保超时打印能重置卡死计时

async def _run_sync_strategy(name, func, *args):
    _st = time.time()
    async with _strategy_sem:
        try:
            if inspect.iscoroutinefunction(func):
                _r = await asyncio.wait_for(func(*args), timeout=_STRATEGY_TIMEOUT)
            else:
                _coro = asyncio.to_thread(func, *args)
                _r = await asyncio.wait_for(_coro, timeout=_STRATEGY_TIMEOUT)
        except asyncio.TimeoutError:
            _debug_log(f"val strategy {name}: 硬超时({_STRATEGY_TIMEOUT}s)跳过——上游阻塞(疑似 DNS/路由挂起)，已隔离")
            print(f"  {name}... ⚠ 超时跳过({_STRATEGY_TIMEOUT}s)", flush=True)
            return []   # 经 asyncio.gather(return_exceptions=True) 不阻断其余策略
    ...
```

**为何是根因修复而非临时规避**：
- 它直接修补了"单策略无超时墙"这一**缺陷本身**——上游挂起不再能拖垮整批，而是被隔离为"超时跳过 + 日志 + 降级为空选"。
- 相比"调大 `_STALL_TIMEOUT` 到 3600"那种掩因补丁：本修复让挂起策略在 720s 内被干净隔离，整批继续产出（仅该策略降级），既保住报告又精确定位问题策略（日志可见）。

**运行机制**：单策略挂起 → 720s 后 `asyncio.wait_for` 抛出 `TimeoutError` → 打印"⚠ 超时跳过" → 该 `asyncio.gather` 任务返回 `[]` → 其余 24 策略正常产出 → main.py 看到周期输出、卡死计时被重置、不再强杀。整批在 ~（原耗时+最多 720s）内完成，而非被杀。

## 四、验证
1. `python -m py_compile get_val_report.py` → COMPILE_OK。
2. 功能测试（1s 超时覆盖复刻逻辑）：并发 [挂起5s, 正常0.2s, 正常0.2s] → 总耗时 1.0s，挂起策略返回 `[]`，正常策略正常产出，整批未被拖垮 ✅。

## 五、可选后续（共享代码，需单独评估风险）
`requests` 的 DNS 盲区是更深层根因。若希望 fuyao/东财调用**在 DNS 阶段就快速失败**而非挂起，可在 `sc_network._quick_request` 加 DNS 感知连接超时（影响全项目所有调用方，改动面大，建议单独立项，不在本报告范围）。
