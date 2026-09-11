# val 超时根因修复（续）：fallback 审计接入 + DNS 解析超时护栏

日期：2026-09-09｜关联根因报告：`20260909_val_timeout_rootcause.md`（提交 `e20ab11`）。
本文件记录用户同意后的两项追加修复：① 策略级超时降级接入统一 fallback 审计；② 在 `sc_network._quick_request`/`em_get` 加 DNS 解析阶段硬超时护栏。

## 背景回顾
上一轮已定位根因：`_run_sync_strategy` 缺每策略硬超时墙 + `requests.timeout` 不覆盖 DNS 解析 → 上游 DNS/路由间歇挂起时 `asyncio.gather` 整批停滞 → main.py 900s 强杀(-1)。并加 `_STRATEGY_TIMEOUT=720s` 的 `asyncio.wait_for` 墙（隔离单策略挂起）。

用户追问"val 有那么多 fallback，为何没兜底"——经盘点，val **确有**多层 exception-based fallback（fuyao `_fuyao_raw` 的 `except→None`、策略层 try/except、`core.data_provider` 的源降级 `_fallback_logger`），但**全部只对异常有效，对"挂起（不抛异常）"无效**。本文件两项修复即补上"挂起→异常"的转换与审计接入。

## 修复一：策略级超时降级接入统一 fallback 审计
**文件**：`get_val_report.py`
- 新增导入 `from stock_common.sc_network import _fallback_logger`。
- `_run_sync_strategy` 的 `asyncio.TimeoutError` 分支（原仅 `_debug_log` + 打印）**增加 `_fallback_logger.warning(...)`**，记录"策略级超时降级"事件。

**作用**：使"策略级超时降级"这一既有 fallback 路径产生的降级事件，能被项目统一的 `fallback` logger 检索/监控，与 `core/data_provider` 等处的源降级审计对齐。属于**观测/可观测性**补全，不影响降级行为本身。

## 修复二：DNS 解析阶段硬超时护栏（从源头让挂起快速失败）
**文件**：`stock_common/sc_network.py`（共享网络层，被 fuyao `_fuyao_raw` 经 `_quick_request`、东财 `em_get` 共同调用）
- 新增模块级 helper `_resolve_host_with_timeout(host, timeout=5.0)` + 带 TTL(300s) 的 `_DNS_CACHE`：
  - 已为 IP 的 host 跳过；
  - 缓存命中仅做字典查找（零额外 DNS 查询，避免热路径每请求真实解析的性能回归）；
  - 缓存失效时，用**独立线程 + `join(timeout)`** 给 `socket.gethostbyname` 加墙：解析挂起（超时不返回）→ 抛 `requests.exceptions.ConnectionError`；解析失败（NXDOMAIN 等）→ 同样抛 `ConnectionError`。
- 在 `_do_request`（实际 `Session.get/post` 之前，位于既有 `try` 内）与 `em_get`（实际 `EM_SESSION.get` 之前，位于既有 `try` 内）各插入 `_resolve_host_with_timeout(domain)` 调用。

**作用（根因级）**：把"DNS 解析挂起"在源头（≤5s）转换为 `ConnectionError` 异常，**直接落入既有 fallback 路径**：
- `_do_request` 的 `except (ConnectionError, ReadTimeout, ConnectTimeout, ProxyError)`（原 849 行）→ 重试 → 最终 `return None` → `_fuyao_raw` 捕获 → `get_fuyao_valuation` 返回 `[]` → 策略25 降级为空选；
- `em_get` 的 `ConnectionError` 分支 → `_record_em_disconnect` → 标记封禁跳过 / 返回 None。
- 即：上游 DNS 挂起从"无限阻塞直到 720s 墙（或永久）"变为"≤5s（冷缓存）快速失败并走既有降级"。720s 策略墙仍是最终兜底（覆盖缓存 TTL 窗口内的罕见盲区）。

## 验证
1. `python -m py_compile get_val_report.py stock_common/sc_network.py` → COMPILE_OK。
2. `from stock_common.sc_network import _fallback_logger` → 无循环依赖（OK）。
3. DNS 护栏功能测试：
   - 正常主机解析 0.028s 成功并缓存；
   - 缓存命中 0.0000s 瞬返（无额外 DNS 查询）；
   - 不可解析主机 0.12s 抛 `ConnectionError`；
   - 清空缓存后模拟 `gethostbyname` 阻塞 30s：5.01s 被超时墙捕获抛 `ConnectionError: DNS resolution timeout (>=5.0s)` ✅。
4. 策略级超时隔离逻辑（上一轮已测）：1s 覆盖下并发[挂起,正常×2] → 挂起返回 `[]`、其余正常、整批未被拖垮 ✅。

## 风险与边界
- `sc_network.py` 为共享热路径模块。护栏采用 TTL 缓存，命中时零额外 DNS 开销；仅缓存失效（≤每 5 分钟每 host 一次）才做真实解析。对正常流量**无性能回归**。
- DNS 护栏的 5s 超时与 720s 策略墙形成**双层防御**：前者快速失败（常态），后者兜底（盲区/多线程泄漏）。
- `_resolve_host_with_timeout` 抛 `ConnectionError`（标准 requests 异常类型），与既有重试/降级逻辑完全兼容，不引入新异常分支。
