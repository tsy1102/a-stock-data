# sc_datasource.py 代码审查报告

## 概述
`stock_common/sc_datasource.py` 负责多种数据源（东财、巨潮、TDX 等）的查询、缓存与聚合，是项目的核心数据层。

## 关键问题

### 类型检查 (mypy)
- 多处函数返回 `Any`，未提供明确的返回类型（例如第 853‑905 行），导致类型安全缺失。
- `asyncio.to_thread` 包装的函数签名不匹配：期望返回 `list[dict[str, Any]]`，但实际返回 `dict[str, Any]`（第 1343‑1345 行）。
- 变量缺少显式注解（`rows`、`_cfg_sc` 等），以及未标注的函数（`_scoring`、`holder_change` 等）。

### 性能瓶颈
- 该模块大量使用同步的 HTTP 请求（`_request_with_retry`）通过 `asyncio.to_thread` 包装为异步，仍然会阻塞线程池，限制并发度。建议改为原生 `aiohttp` 异步请求。
- 缓存层已使用 SQLite，但仍频繁在单次调用中重新读取/写入，导致 I/O 开销。可以在函数内部使用 `@cached` 装饰缓存结果。

## 改进建议
1. **完善类型注解**：为所有公开函数添加完整的返回类型，如 `dict[str, Any]` 或 `list[dict[str, Any]]`，避免使用 `Any`。
2. **统一异步网络层**：在 `sc_network.py` 中实现 `async_fetch`（使用 `aiohttp`），让 `sc_datasource` 直接调用异步接口，移除 `asyncio.to_thread` 包装。
3. **缓存优化**：对频繁调用的函数（如 `holder_change`、`get_holder_structure`）使用 `@cached`，并设置合理的 TTL，减少 SQLite 读写。
4. **错误处理**：在网络请求中加入超时重试和明确的异常捕获，避免返回 `None` 导致后续 `NoneType` 错误。
5. **代码风格**：目前 `flake8` 对该文件无明显错误，保持现有代码格式即可。

---

如需进一步的重构实现计划或具体的类型注解示例，请告诉我！
